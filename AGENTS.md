# Agentdots repository instructions

Agentdots owns portable agent skills and the shared rules installed into
agent clients. `README.md` covers installation, targets, and recovery.
These instructions apply to developing this repository.

## Ownership and instruction sources

- `instructions/global.md` is the shared policy installed into clients.
  Repository-specific commands and development details belong in `AGENTS.md`.
- `CLAUDE.md` is a relative symlink to this file. Global installation must
  never link a client to this repository's `AGENTS.md` or `CLAUDE.md`.
- `lib/targets.sh` defines the global instruction source and client targets.
  Keep installation, diagnostics, and recovery documentation consistent with it.
- Reusable skills live under `skills/<name>/`; procedures specific to another
  repository belong in that repository's `.agents/skills/`.
  Every directory under `skills/` is active and must pass package validation;
  keep drafts elsewhere. `scripts/validate-skills.py` is the shared validation
  entrypoint used by installation and diagnostics.
- Backups and client state stay local. Follow the shared rules about secrets
  and Git authorization; leave changes uncommitted unless asked to commit.

## Plan substantive changes

For requested planning, use `plan-change`; for requested working-change review,
use `review-changes`. See [the workflow](docs/workflows/plan-build-review.md)
for a manual handoff between a builder and a separate reviewer.

Use [the task brief](docs/templates/task-brief.md) to make the requested
outcome, scope, acceptance criteria, and evidence explicit. It can live in
an existing issue or plan; a new file is not required for every change.

## Verify a change

```bash
./test.sh            # isolated regression fixtures; no client installation
./sync.sh            # after changing installed sources or client targets
./doctor.sh          # read-only; success ends with "All checks passed."
```

`sync.sh` changes the live client links and `~/.dotfiles-env.sh`; run tests
before installing. Test fixtures must route targets into temporary directories
without changing `HOME` or touching real client paths. Preserve the portable
skill schema and use the existing installer rather than adding another one.
