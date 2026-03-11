## Session Plan

### Task 1: Add observability skill (Actuator, Micrometer, OTEL tracing)
Files: skills/observability/SKILL.md (new)
Description: Create a new observability skill covering Spring Boot Actuator configuration, Micrometer metrics (counters, timers, gauges), OpenTelemetry distributed tracing setup, structured logging with MDC/traceId correlation, health indicators, and production-ready monitoring patterns. This is a complete gap — real Spring Boot services in prod need this.
Issue: none

### Task 2: Expand spring-boot skill with modern Java patterns
Files: skills/spring-boot/SKILL.md
Description: Add sections for: (1) Java Records as DTOs — replacing Lombok for immutable value objects, (2) RestClient (Spring 3.2+) replacing RestTemplate with fluent API and error handling, (3) Virtual threads configuration (`spring.threads.virtual.enabled=true`), when to use/avoid, (4) Pagination patterns — Pageable, Page<T>, slice queries, (5) OpenAPI/Swagger with springdoc-openapi-starter-webmvc-ui, (6) @Cacheable / @CacheEvict with Caffeine and Redis config.
Issue: none

### Task 3: Expand testing skill with missing patterns
Files: skills/testing/SKILL.md
Description: Add sections for: (1) WireMock for mocking external HTTP services in integration tests, (2) Parameterized tests with @ParameterizedTest / @MethodSource / @CsvSource, (3) Security slice testing — MockMvc with @WithMockUser and custom security configs, (4) @TestConfiguration for replacing beans in test context, (5) Test data builders / object mother pattern to reduce fixture boilerplate.
Issue: none

### Task 4: Expand code-review skill with concurrency and modern Java guidance
Files: skills/code-review/SKILL.md
Description: Add sections for: (1) Concurrency review checklist — shared mutable state, improper use of synchronized, thread-safe collections, (2) Virtual threads pitfalls — pinning (synchronized blocks, ThreadLocal), carrier thread blocking, (3) Records vs Lombok — when to use each, (4) Reactive pitfalls — blocking calls in reactive chains, missing error operators, backpressure.
Issue: none

### Task 5: Expand java-build skill with static analysis and native image
Files: skills/java-build/SKILL.md
Description: Add sections for: (1) Checkstyle and SpotBugs/PMD integration via Maven plugins — how to run and interpret output, (2) GraalVM native image build with Spring AOT (`./mvnw -Pnative native:compile`), (3) Build profiles — dev vs prod, (4) Dependency vulnerability scanning with OWASP dependency-check plugin.
Issue: none

### Issue Responses
(No issues today)

---

Priority reasoning:
1. Observability is a complete gap — every prod Spring Boot service needs Actuator + metrics + tracing
2. Modern Java patterns (Records, RestClient, virtual threads) are what developers hit daily in Spring Boot 3.2+
3. Testing gaps (WireMock, parameterized, security) are high-frequency pain points
4. Code review additions (concurrency, reactive pitfalls) prevent critical bugs
5. Build skill additions (static analysis, native image) round out the build workflow
