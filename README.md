# java-agent

A self-evolving AI agent for Java/Spring Boot development. Powered by [Claude Code](https://claude.ai/code) — works with your Claude Code Pro subscription, no API key needed.

Every 8 hours, a GitHub Actions cron job runs the agent. It reads its own skills, identifies gaps, improves itself, and commits the changes — if the build passes. It also monitors and responds to GitHub issues.

## Quick Start

### Implement a feature in your Java project

```bash
./scripts/evolve.sh ~/code/your-project -p "add JWT authentication"
```

The agent will:
1. Run Claude Code against your project
2. Implement the requested feature
3. Verify the build passes (Maven or Gradle)
4. Commit the changes (or revert if the build breaks)

### Run an autonomous evolution cycle

```bash
./scripts/evolve.sh
```

This triggers the full 3-phase pipeline where the agent improves its own skills.

### Run against a specific project (no prompt)

```bash
./scripts/evolve.sh ~/code/your-project
```

## Skills

The agent carries domain expertise as markdown files in `skills/`:

| Skill | What it covers |
|-------|---------------|
| `java-build` | Maven & Gradle build, test, lint workflows |
| `spring-boot` | Spring Boot 3.x — REST, JPA, Security 6.x, WebFlux, config |
| `testing` | JUnit 5, Mockito, @WebMvcTest, @DataJpaTest, Testcontainers |
| `code-review` | SOLID principles, clean code, security review |
| `observability` | Actuator, Micrometer metrics, OpenTelemetry tracing |
| `database-migrations` | Flyway, Liquibase, rollback strategies, migration testing |
| `messaging` | Kafka producers/consumers, dead-letter topics, idempotent consumers |

These skills are what the agent evolves — each cycle it assesses gaps and adds or improves them.

## How It Works

The evolution loop (`scripts/evolve.sh`) runs a 3-phase pipeline using the `claude` CLI:

1. **Setup** — Verifies build, fetches GitHub issues via `gh` CLI
2. **Phase A (Plan)** — Claude reads all skills, journal, and issues, then writes a `SESSION_PLAN.md`
3. **Phase B (Implement)** — Claude executes each planned task (15 min per task)
4. **Phase C (Respond)** — Extracts and posts responses to GitHub issues
5. **Verify** — Checks build passes, reverts if broken, pushes

## State Files

| File | Purpose |
|------|---------|
| `JOURNAL.md` | Chronological log of evolution sessions |
| `LEARNINGS.md` | Self-reflections and lessons learned |
| `DAY_COUNT` | Current evolution day counter |
| `IDENTITY.md` | Agent constitution and rules (protected) |
| `PERSONALITY.md` | Voice and values (protected) |

## Safety

- Protected files (`IDENTITY.md`, `PERSONALITY.md`, `scripts/`, `.github/workflows/`) cannot be modified by the agent
- Every change must pass the Java build before being committed
- Failed builds are automatically reverted
- Issue text is treated as untrusted input
- Tests are never deleted

## GitHub Pages

The agent's journal is published at the repo's GitHub Pages site. Updated automatically after each evolution cycle via `scripts/build_site.py`.

## Setup Your Own

1. Fork this repo
2. Enable GitHub Actions and GitHub Pages (from `docs/` folder)
3. The agent runs automatically every 8 hours using your GitHub Actions minutes
4. Open issues to request features or skills — the agent reads and responds to them
