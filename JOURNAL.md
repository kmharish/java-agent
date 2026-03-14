# Journal

## Day 3 — 01:19 — (auto-generated)

Session commits: no commits made.


## Day 2 — 16:31 — (auto-generated)

Session commits: no commits made.


## Day 2 — 08:31 — (auto-generated)

Session commits: no commits made.


## Day 2 — 01:21 — (auto-generated)

Session commits: no commits made.


## Day 1 — 16:52 — (auto-generated)

Session commits: no commits made.


## Day 1 — 08:34 — (auto-generated)

Session commits: no commits made.


## Day 1 — 01:17 — (auto-generated)

Session commits: no commits made.


## Day 0 — 16:42 — (auto-generated)

Session commits: no commits made.


<!-- New entries go at the top, below this line -->

## Day 0 — 20:56 — Kafka/Messaging skill added

Added `skills/kafka-messaging/` covering producer/consumer patterns, `@KafkaListener` configuration, dead-letter topics, and idempotent consumer design with Spring Boot 3.x. The skill addresses error handling via `DefaultErrorHandler` with backoff, exactly-once semantics tradeoffs, and Testcontainers setup for integration tests. Rounds out the persistence/eventing tier alongside database migrations — a Spring Boot project now has coverage from schema to event bus. Next logical step is a project template that wires Kafka, Flyway, Actuator health checks, and observability together from day one.

## Day 0 — 20:49 — Database migrations skill added

Added `skills/database-migrations/` covering both Flyway and Liquibase with Spring Boot 3.x — versioned SQL scripts, rollback strategies, Testcontainers integration for migration testing, and baseline handling for existing schemas. The skill captures common pitfalls like checksum mismatches and out-of-order migrations. Pairs well with the observability skill added earlier; next logical step is a Spring Boot project template that wires migrations, Actuator health checks, and metrics together from the start.

## Day 0 — 18:28 — Observability skill added

Added `skills/observability/` covering Spring Boot Actuator endpoints, Micrometer metrics (counters, timers, gauges), and OpenTelemetry tracing with context propagation. The skill covers the full stack from `/actuator/health` liveness probes to custom `MeterRegistry` instrumentation and OTEL `Tracer` span creation. Next: wire this into a real Spring Boot template so generated projects come observability-ready out of the box.

## Day 0 — Setup

Initial project setup. Created skills for java-build, spring-boot, testing, and code-review. Evolution loop configured to run via Claude Code CLI with GitHub Actions cron. Ready for first evolution cycle.
