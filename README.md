# gitwise

> AI-powered git commit messages that learn your repo's style.

Most commit message generators produce the same generic output every time. **gitwise** reads your last 10 commits, detects your team's format (Conventional Commits, Gitmoji, or plain), and generates a message that actually fits — then lets you approve, regenerate, or edit before anything is saved.

---

## What makes it different

| Feature | gitwise | Others |
| --- | --- | --- |
| Learns your repo's commit style | ✅ | ❌ |
| Detects tech stack for context | ✅ | ❌ |
| Interactive: accept / regenerate / edit | ✅ | Rarely |
| Warns when diff should be split | ✅ | ❌ |
| Smart diff compression (fewer tokens) | ✅ | Partial |
| Claude + OpenAI support | ✅ | Varies |
| Dry run mode | ✅ | Rare |

---

## Demo

```text
$ gitwise

──────────────────────────── gitwise ─────────────────────────────
  Stack:   Python
  Style:   conventional
  Files:   gitwise/cli.py, gitwise/context.py
  Backend: claude

╭──────────────────── Generated Commit Message ────────────────────╮
│                                                                   │
│  feat(cli): add interactive accept/regenerate flow                │
│                                                                   │
│  Replaces single-shot generation with a looped prompt so users   │
│  can regenerate or edit before committing.                        │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯

  [a] Accept & commit   [r] Regenerate   [e] Edit   [q] Quit
```

---

## Installation

**Mac / Linux:**

```bash
git clone https://github.com/TheChyeahhh/gitwise.git
cd gitwise
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Windows (Command Prompt or PowerShell):**

```bash
git clone https://github.com/TheChyeahhh/gitwise.git
cd gitwise
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

---

## Setup

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here    # console.anthropic.com
OPENAI_API_KEY=sk-your-key-here           # platform.openai.com
AI_BACKEND=claude
```

> Your key is stored only in `.env` and is blocked from commits by `.gitignore`.

---

## Usage

```bash
cd your-project
git add .
gitwise
```

### Options

```bash
gitwise --backend openai          # use OpenAI instead of Claude
gitwise --style conventional      # force Conventional Commits format
gitwise --style gitmoji           # force Gitmoji format
gitwise --style plain             # force plain format
gitwise --dry-run                 # preview message without committing
gitwise --yes                     # skip prompt, commit immediately
```

---

## How style detection works

gitwise reads your last 10 commit messages and detects the pattern:

- 40%+ match `feat:` / `fix:` / `chore:` → **Conventional Commits**
- 40%+ start with an emoji → **Gitmoji**
- Otherwise → **plain**

Override anytime with `--style`.

---

## Requirements

- Python 3.9+
- Git
- A [Claude API key](https://console.anthropic.com) or [OpenAI API key](https://platform.openai.com)

---

## Future Ideas

- `gitwise hook` — install as a `prepare-commit-msg` git hook
- `.gitwise.yaml` — per-repo config for team conventions
- `gitwise split` — auto-split large diffs into logical commits
- Changelog generation from commit history
- GitHub Actions integration

---

## License

MIT
