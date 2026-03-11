# CLAUDE.md

## What This Is

A self-evolving AI agent for Java/Spring Boot development. Powered by Claude Code CLI — no API key needed, works with your Claude Code Pro subscription.

A GitHub Actions cron job (`scripts/evolve.sh`) runs every 8 hours using a 3-phase pipeline (plan → implement → respond). The agent reads its own skills, picks improvements, implements them, and commits — if everything passes.

## How to Run

### Interactive (just use Claude Code in your Java project)
```bash
cd your-java-project
claude  # Claude Code already knows Java — the skills here make it better
```

### Run an evolution cycle manually
```bash
./scripts/evolve.sh
```

### Run against a specific Java project
```bash
./scripts/evolve.sh /path/to/java/project
```

## Architecture

**Skills** (`skills/`): Markdown files with domain expertise loaded into prompts.
- `java-build/` — Maven & Gradle build, test, lint workflows
- `spring-boot/` — Spring Boot 3.x patterns, WebFlux, Security, JPA
- `testing/` — JUnit 5, Mockito, integration testing, Testcontainers
- `code-review/` — SOLID principles, clean code, security review

**Evolution loop** (`scripts/evolve.sh`): 3-phase pipeline using `claude` CLI:
1. Verifies build → fetches GitHub issues via `gh` CLI
2. **Phase A** (Planning): Claude reads everything, writes `SESSION_PLAN.md`
3. **Phase B** (Implementation): Claude executes each task (15 min each)
4. **Phase C** (Communication): Extracts and posts issue responses
5. Verifies build, fixes or reverts → pushes

**State files** (read/written by the agent during evolution):
- `IDENTITY.md` — the agent's constitution and rules (DO NOT MODIFY)
- `PERSONALITY.md` — voice and values (DO NOT MODIFY)
- `JOURNAL.md` — chronological log of evolution sessions (append at top)
- `LEARNINGS.md` — self-reflections and lessons learned
- `DAY_COUNT` — integer tracking current evolution day
- `SESSION_PLAN.md` — ephemeral, written by Phase A (gitignored)
- `ISSUES_TODAY.md` — ephemeral, generated during evolution (gitignored)
- `ISSUE_RESPONSE.md` — ephemeral, agent writes to respond to issues (gitignored)

## Safety Rules

Enforced by `evolve.sh`:
- Never modify `IDENTITY.md`, `PERSONALITY.md`, `scripts/evolve.sh`, `scripts/format_issues.py`, or `.github/workflows/`
- Every change must pass the Java build (`mvn test` / `gradle build`)
- If build fails after changes, revert with `git checkout -- skills/ templates/`
- Never delete existing tests
- Multiple tasks per evolution session, each verified independently
