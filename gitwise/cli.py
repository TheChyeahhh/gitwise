import os
import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.prompt import Prompt
from dotenv import load_dotenv

from .git_ops import (
    get_repo_root,
    get_staged_diff,
    get_staged_files,
    get_recent_commits,
    do_commit,
    compress_diff,
    detect_stack,
)
from .context import detect_commit_style, build_prompt
from .ai import generate

load_dotenv()
console = Console()

LARGE_DIFF_THRESHOLD = 300  # lines


def warn_large_diff(files: list[str], line_count: int):
    console.print()
    console.print(
        Panel(
            f"[yellow]Your diff spans [bold]{line_count} lines[/bold] across [bold]{len(files)} files[/bold].[/yellow]\n\n"
            "Large diffs produce vague messages. Consider splitting into smaller commits:\n"
            + "\n".join(f"  [dim]{f}[/dim]" for f in files),
            title="[bold yellow]⚠ Large Diff Detected[/bold yellow]",
            border_style="yellow",
        )
    )
    if not click.confirm("  Continue and generate one message anyway?", default=True):
        sys.exit(0)


def interactive_loop(message: str, prompt_text: str, backend: str) -> str | None:
    """Show message and let the user accept, regenerate, edit, or quit."""
    while True:
        console.print()
        console.print(
            Panel(
                Text(message, style="bold white"),
                title="[bold cyan]Generated Commit Message[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print()
        console.print("  [bold green][a][/bold green] Accept & commit   "
                      "[bold yellow][r][/bold yellow] Regenerate   "
                      "[bold blue][e][/bold blue] Edit   "
                      "[bold red][q][/bold red] Quit")
        console.print()

        choice = click.getchar().lower()

        if choice == "a":
            return message
        elif choice == "r":
            console.print()
            with console.status("[bold green]Regenerating...[/bold green]"):
                message = generate(prompt_text, backend)
        elif choice == "e":
            console.print()
            edited = click.edit(message)
            if edited:
                message = edited.strip()
            return message
        elif choice in ("q", "\x03"):
            console.print("\n[dim]Aborted.[/dim]")
            return None


@click.command()
@click.option(
    "--backend", "-b",
    default=None,
    type=click.Choice(["claude", "openai"], case_sensitive=False),
    help="AI backend (claude or openai). Defaults to AI_BACKEND env var or claude.",
)
@click.option(
    "--style", "-s",
    default=None,
    type=click.Choice(["conventional", "gitmoji", "plain", "auto"], case_sensitive=False),
    help="Commit message style. Default: auto-detect from repo history.",
)
@click.option(
    "--dry-run", "-d",
    is_flag=True,
    default=False,
    help="Generate and show the message without committing.",
)
@click.option(
    "--yes", "-y",
    is_flag=True,
    default=False,
    help="Skip interactive prompt and commit immediately.",
)
def main(backend: str, style: str, dry_run: bool, yes: bool):
    """AI-powered git commit messages that learn your repo's style.

    \b
    Run inside any git repo with staged changes:
      gitwise
      gitwise --style conventional
      gitwise --backend openai
      gitwise --dry-run
    """
    # Resolve backend
    selected_backend = backend or os.getenv("AI_BACKEND", "claude").lower()

    # Validate git repo
    root = get_repo_root()
    if not root:
        console.print("[bold red]Error:[/bold red] Not inside a git repository.")
        sys.exit(1)

    # Get staged diff
    diff = get_staged_diff()
    if not diff:
        console.print("[bold red]Nothing staged.[/bold red] Stage your changes first with [bold]git add[/bold].")
        sys.exit(1)

    staged_files = get_staged_files()
    diff_lines = len(diff.splitlines())

    # Warn on large diffs
    if diff_lines > LARGE_DIFF_THRESHOLD:
        warn_large_diff(staged_files, diff_lines)

    # Gather context
    recent_commits = get_recent_commits(10)
    stack = detect_stack(root)

    # Detect or use provided style
    resolved_style = style if style and style != "auto" else detect_commit_style(recent_commits)

    # Show what we detected
    console.print()
    console.print(Rule("[dim]gitwise[/dim]"))
    console.print(f"  [dim]Stack:[/dim]  {', '.join(stack)}")
    console.print(f"  [dim]Style:[/dim]  {resolved_style}")
    console.print(f"  [dim]Files:[/dim]  {', '.join(staged_files)}")
    console.print(f"  [dim]Backend:[/dim] {selected_backend}")
    console.print()

    # Compress diff and build prompt
    compressed = compress_diff(diff)
    prompt_text = build_prompt(compressed, recent_commits, stack, resolved_style)

    # Generate
    with console.status("[bold green]Generating commit message...[/bold green]"):
        try:
            message = generate(prompt_text, selected_backend)
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            sys.exit(1)

    # Dry run — just show and exit
    if dry_run:
        console.print(
            Panel(
                Text(message, style="bold white"),
                title="[bold cyan]Generated Commit Message[/bold cyan] [dim](dry run)[/dim]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print()
        return

    # Auto-commit with --yes
    if yes:
        ok, output = do_commit(message)
        if ok:
            console.print(f"\n[bold green]✓ Committed:[/bold green] {message}\n")
        else:
            console.print(f"\n[bold red]Commit failed:[/bold red] {output}\n")
        return

    # Interactive flow
    final_message = interactive_loop(message, prompt_text, selected_backend)
    if final_message is None:
        return

    ok, output = do_commit(final_message)
    if ok:
        console.print(f"\n[bold green]✓ Committed:[/bold green] {final_message}\n")
    else:
        console.print(f"\n[bold red]Commit failed:[/bold red] {output}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
