# Journal

<!-- New entries go at the top, below this line -->

## Day 0 — 18:28 — Observability skill added

Added `skills/observability/` covering Spring Boot Actuator endpoints, Micrometer metrics (counters, timers, gauges), and OpenTelemetry tracing with context propagation. The skill covers the full stack from `/actuator/health` liveness probes to custom `MeterRegistry` instrumentation and OTEL `Tracer` span creation. Next: wire this into a real Spring Boot template so generated projects come observability-ready out of the box.

## Day 0 — Setup

Initial project setup. Created skills for java-build, spring-boot, testing, and code-review. Evolution loop configured to run via Claude Code CLI with GitHub Actions cron. Ready for first evolution cycle.
