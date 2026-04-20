from __future__ import annotations

import subprocess
import os
from pathlib import Path


def run(cmd: list[str], cwd: str = None) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd(),
    )
    return result.stdout.strip()


def get_repo_root() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def get_staged_diff() -> str:
    return run(["git", "diff", "--staged"])


def get_staged_files() -> list[str]:
    output = run(["git", "diff", "--staged", "--name-only"])
    return [f for f in output.splitlines() if f]


def get_recent_commits(n: int = 10) -> list[str]:
    output = run(["git", "log", f"--max-count={n}", "--pretty=format:%s"])
    return [line for line in output.splitlines() if line]


def do_commit(message: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, result.stdout.strip()
    return False, result.stderr.strip()


def compress_diff(diff: str, max_lines: int = 400) -> str:
    """Strip noise from diff and truncate to max_lines to save tokens."""
    lines = diff.splitlines()
    cleaned = []
    for line in lines:
        # Skip binary markers, index lines, and mode change lines
        if any(line.startswith(p) for p in ("index ", "old mode", "new mode", "Binary")):
            continue
        cleaned.append(line)

    if len(cleaned) <= max_lines:
        return "\n".join(cleaned)

    # Keep first max_lines and note truncation
    truncated = cleaned[:max_lines]
    truncated.append(f"\n... [diff truncated: {len(cleaned) - max_lines} more lines] ...")
    return "\n".join(truncated)


def detect_stack(root: str) -> list[str]:
    """Detect tech stack from files in the repo root."""
    root_path = Path(root)
    markers = {
        "package.json": "Node.js",
        "requirements.txt": "Python",
        "pyproject.toml": "Python",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "pom.xml": "Java/Maven",
        "build.gradle": "Java/Gradle",
        "composer.json": "PHP",
        "Gemfile": "Ruby",
        "mix.exs": "Elixir",
        "pubspec.yaml": "Dart/Flutter",
        "Dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
        ".terraform": "Terraform",
        "next.config.js": "Next.js",
        "next.config.ts": "Next.js",
        "vite.config.ts": "Vite",
        "vite.config.js": "Vite",
        "tailwind.config.js": "Tailwind CSS",
        "tailwind.config.ts": "Tailwind CSS",
    }
    detected = []
    for filename, label in markers.items():
        if (root_path / filename).exists() and label not in detected:
            detected.append(label)
    return detected or ["Unknown"]
