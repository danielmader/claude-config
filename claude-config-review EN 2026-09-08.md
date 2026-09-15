# Review of Simon Blauth's claude-config

Date: 2026-09-08
Reviewer: Claude, on Daniel Mader's machine
Scope: all skills, patches, cc.py, settings.json, CLAUDE.md; drift check run with network access
State: nothing installed or changed on this machine

## Verdict

The setup is well built and worth adopting. A few things need to be sorted out before running `install`.

## What cc.py actually does

It does not sync via git. It has three separate flows:

- **vendor** clones the upstream skill repos (superpowers, mattpocock, pstack, JuliusBrussee), copies the chosen skill directories into `skills/` under Simon's own names, applies his `patches/*.patch`, and records the upstream commit and a content hash in `sources.tsv`.
- **install** copies `skills/`, `rules/`, `CLAUDE.md`, and a rendered `settings.json` into `~/.claude`. Plain copies, no symlinks, so it works on Windows.
- **check** reports drift in three directions and changes nothing: repo dirty or behind origin, installed files differing from the repo, upstream skills moved past the pinned hash. It runs once a day from a SessionStart hook.

Moving changes between Daniel and Simon is ordinary git push and pull on the repo itself.

## What is good

- **cc.py itself** is clean: dataclasses, type annotations, small functions, no auto-apply anywhere. It matches the conventions in Daniel's own CLAUDE.md. The patch mechanism for upstream edits and the pinned hashes are sensible.
- **The full check with network access** shows no upstream drift. All 18 pins are at upstream HEAD as of today.
- **Skill quality is high.** The writing skills (unslop, technical-writing, writing-for-agents) are dense and useful. systematic-debugging and verification-before-completion are solid, and Simon's patch adds commit-content and signature checks. grilling is small and sharp. The heavy ones (deslopify, prune-docs, improve-codebase-architecture) are user-invoked only, so they cost no context until called.
- **The root CLAUDE.md** is thoughtful. The "surface friction, don't absorb it" and "no speculative doc claims" sections are rules worth having on any project.

## Problems to resolve before installing

1. **Install overwrites Daniel's own config.** His `~/.claude/CLAUDE.md` (the find/xargs and git -C rules) and his entire permission allowlist (the `git -C` forms, Windows Read paths, pytest commands, `switchModelsOnFlag`) live nowhere in the repo. Only `model` and `effortLevel` survive. Move the shell rules to `~/.claude/rules/shell.md` first, which install leaves alone, or propose them into the shared CLAUDE.md since they are general. The README admits settings.json has no local override, which is the real gap for two people sharing one repo.

2. **settings.json carries Simon's personal choices.** It denies `pwsh` and `powershell.exe`, which may bite on Windows, and `az`. It forces fullscreen TUI, disables auto memory, and drops the Co-Authored-By trailer. Decide which of these are wanted.

3. **Collaboration model is undecided.** Daniel's clone points straight at Simon's GitHub repo. Any local commit will be reported as "ahead, not pushed" every day, and pushing is not possible. Either fork and add Simon's repo as upstream, or agree on pull-only.

4. **Root CLAUDE.md contains Simon-specific claims.** It says GPG signing is configured. Daniel's git config has no signing set up, so that line is false for him. It also references `glab` and Azure workflows.

5. **Run install with the system Python.** On this machine `python3` resolves to `~/devel/.venv/bin/python3`, so the hook command would depend on that venv existing. The repo's own `.claude/CLAUDE.md` warns about exactly this.

## Suitability judgment calls

- **tdd is strict.** "No production code without a failing test first. Wrote code first? Delete it." Examples are TypeScript and npm. For PyQt GUI work in beam_analyzer and ruby_array, test-first on widgets is often impractical. The skill permits exceptions on request, but the CLAUDE.md routes every implementation to it. Worth discussing with Simon.
- **reflect has loose ends.** It cites `plugin-dev:skill-development` and `encode-lessons-in-structure`, neither of which is vendored, and cc.py's dangling-reference detector does not catch that syntax. It needs `node`, which is not on this machine. It also says backlog items get filed to a tracker "automatically", which contradicts the repo's own rule against unrequested remote writes.
- **Upstream clutter gets installed.** The `agents/openai.yaml` files and systematic-debugging's `test-pressure-*.md` are Codex metadata and upstream test fixtures. Harmless and not loaded into context, but they land in `~/.claude/skills`.
- **cc.py has no tests**, which sits oddly beside a CLAUDE.md that mandates TDD.

## Next steps

Decide fork vs. pull-only and what to do with the existing rules. Then create the `~/.claude/rules/` file and run install with `/usr/bin/python3`.
