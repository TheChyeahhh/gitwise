import re


CONVENTIONAL_TYPES = ("feat", "fix", "chore", "docs", "style", "refactor", "test", "perf", "ci", "build", "revert")

GITMOJI_PATTERN = re.compile(r"^[\U00010000-\U0010ffff\u2600-\u27BF]|^:[a-z_]+:")


def detect_commit_style(commits: list[str]) -> str:
    """
    Infer the repo's commit style from recent history.
    Returns: 'conventional', 'gitmoji', or 'plain'
    """
    if not commits:
        return "conventional"

    conventional_count = 0
    gitmoji_count = 0

    for msg in commits:
        msg = msg.strip()
        if re.match(r"^(" + "|".join(CONVENTIONAL_TYPES) + r")(\(.+?\))?!?:", msg):
            conventional_count += 1
        elif GITMOJI_PATTERN.match(msg):
            gitmoji_count += 1

    total = len(commits)
    if conventional_count / total >= 0.4:
        return "conventional"
    if gitmoji_count / total >= 0.4:
        return "gitmoji"
    return "plain"


def style_instructions(style: str) -> str:
    if style == "conventional":
        return (
            "Use Conventional Commits format: type(scope): description\n"
            "Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build\n"
            "Scope is optional — use it when the change is clearly scoped to one area.\n"
            "Example: feat(auth): add JWT token refresh logic"
        )
    if style == "gitmoji":
        return (
            "Start with a gitmoji followed by a short description.\n"
            "Common: ✨ new feature, 🐛 bug fix, 📝 docs, ♻️ refactor, "
            "🚀 deploy, 💄 UI, 🔧 config, ✅ tests, ⚡ performance, 🔒 security\n"
            "Example: ✨ add user profile avatar upload"
        )
    return (
        "Write a plain, clear subject line in imperative mood.\n"
        "Example: Add rate limiting to the authentication endpoint"
    )


def build_prompt(diff: str, recent_commits: list[str], stack: list[str], style: str) -> str:
    commits_block = "\n".join(f"  - {c}" for c in recent_commits) if recent_commits else "  (no prior commits)"
    stack_str = ", ".join(stack)

    return f"""You are an expert software engineer who writes exceptional git commit messages.

Given the staged diff below, write a commit message following these rules:
1. Subject line: max 72 characters, imperative mood ("add" not "adds"), no period at end
2. If the change is complex or non-obvious, add a blank line then a short body explaining WHY
3. Be specific — name the actual function, file, or feature changed
4. Never write vague messages like "update files", "fix stuff", "minor changes", or "various updates"
5. {style_instructions(style)}

Repository context:
- Tech stack: {stack_str}
- Recent commit messages from this repo (match this style and tone):
{commits_block}

Staged diff:
```
{diff}
```

Respond with ONLY the commit message. No explanation. No markdown code fences. No quotes."""
