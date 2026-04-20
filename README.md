# gitwise

> AI-powered git commit messages that learn your repo's style.

Most commit message generators write the same generic output every time. **gitwise** reads your last 10 commits, detects your team's format (Conventional, Gitmoji, or plain), and generates a message that actually fits.

---

## What makes it different

| Feature | gitwise | Others |
| --- | --- | --- |
| Learns your repo's commit style | ✅ | ❌ |
| Detects tech stack for context | ✅ | ❌ |
| Interactive: accept / regenerate / edit | ✅ | Rarely |
| Warns when diff is too large to split | ✅ | ❌ |
| Smart diff compression (fewer tokens) | ✅ | Partial |
| Claude + OpenAI support | ✅ | Varies |
| Dry run mode | ✅ | Rare |

---

## Demo

```
$ gitwise

─────────────────────────── gitwise ────────────────────────────
  Stack:   Python
  Style:   conventional
  Files:   gitwise/cli.py, gitwise/context.py
  Backend: claude

╭─────────────── Generated Commit Message ───────────────╮
│                                                         │
│  feat(cli): add interactive accept/regenerate flow      │
│                                                         │
│  Replaces single-shot generation with a looped          │
│  prompt so users can regenerate or edit before commit.  │
│                                                         │
╰─────────────────────────────────────────────────────────╯

  [a] Accept & commit   [r] Regenerate   [e] Edit   [q] Quit
```

---

## Installation

```bash
git clone https://github.com/TheChyeahhh/gitwise.git
cd gitwise
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

---

## Setup

```bash
cp .env.example .env
```

Open `.env` and add your API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
AI_BACKEND=claude
```

- Get a Claude key at [console.anthropic.com](https://console.anthropic.com)
- Get an OpenAI key at [platform.openai.com](https://platform.openai.com)

> Your key lives in `.env` and is never committed (blocked by `.gitignore`).

---

## Usage

Navigate to any git repo, stage your changes, then run:

```bash
cd your-project
git add .
gitwise
```

### Options

```bash
# Use OpenAI instead of Claude
gitwise --backend openai

# Force a specific style
gitwise --style conventional
gitwise --style gitmoji
gitwise --style plain

# Preview without committing
gitwise --dry-run

# Skip the prompt and commit immediately
gitwise --yes
```

---

## How the style detection works

gitwise reads your last 10 commit messages and counts patterns:

- If 40%+ match `feat:` / `fix:` / `chore:` etc → **Conventional Commits**
- If 40%+ start with an emoji → **Gitmoji**
- Otherwise → **plain**

Override it anytime with `--style`.

---

## How it avoids bad messages

- Reads staged diff and **all** changed filenames
- Detects your tech stack (Node, Python, Go, Rust, Docker, etc.)
- Sends your last 10 commit messages as examples
- Compresses large diffs to reduce noise and token cost
- Warns you if your diff is too large and should be split

---

## Every time you come back

```bash
cd gitwise
source .venv/bin/activate
cd your-project
git add .
gitwise
```

---

## Requirements

- Python 3.9+
- A [Claude API key](https://console.anthropic.com) or [OpenAI API key](https://platform.openai.com)
- Must be run inside a git repository with staged changes

---

## Future Ideas

- `gitwise hook` — install as a `prepare-commit-msg` git hook
- `.gitwise.yaml` per-repo config for team conventions
- `gitwise split` — auto-detect logical commit boundaries in large diffs
- Changelog generation from commit history
- GitHub Actions integration

---

## License

MIT
