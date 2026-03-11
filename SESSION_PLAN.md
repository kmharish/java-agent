## Session Plan

### Task 1: Add Kafka/Messaging Skill
Files: skills/messaging/SKILL.md
Description: Create a new skill covering Spring Kafka patterns for production microservices. Include: producer config (acks, retries, idempotency), consumer config (concurrency, auto-offset-reset, error handlers), @KafkaListener with explicit acknowledgment, dead-letter queue (DLQ) setup, KafkaTemplate usage, deserialization error handling, testing with @EmbeddedKafka and Testcontainers Kafka, common pitfalls (consumer group rebalancing, poison pills, serialization mismatches). Cover both StringSerializer and JSON (Jackson) setups. Include transactional producer pattern for exactly-once semantics.
Issue: none

### Task 2: Add Docker/Containerization Skill
Files: skills/docker/SKILL.md
Description: Create a new skill covering how to properly containerize Spring Boot 3.x apps. Include: multi-stage Dockerfile (build + runtime layers), choosing base image (eclipse-temurin vs distroless vs alpine), JVM flags for containers (UseContainerSupport, MaxRAMPercentage, ExitOnOutOfMemoryError), layered JAR with spring-boot-maven-plugin for better layer caching, health check HEALTHCHECK instruction, non-root user for security, Docker Compose for local dev with dependent services (Postgres, Redis, Kafka), .dockerignore patterns, and BuildKit cache mounts for Maven/Gradle caches.
Issue: none

### Task 3: Enhance Spring Boot Skill with 3.2+ Patterns
Files: skills/spring-boot/SKILL.md
Description: Add a "Spring Boot 3.2+" section covering: virtual threads (spring.threads.virtual.enabled=true and what it means for blocking I/O), RestClient replacing RestTemplate (fluent API, error handling, exchange), @ConfigurationProperties with Java records (immutable config), Problem Details / RFC 7807 error responses (ProblemDetail class, built-in Spring MVC support), and @HttpExchange declarative HTTP clients. These are modern patterns developers actively look for and aren't well-covered in vanilla LLM responses.
Issue: none

### Issue Responses
(no issues today)

Priority:
1. Messaging skill — Kafka is used in nearly every microservices project; the gap is most likely to make a developer choose vanilla Claude over java-agent
2. Docker skill — containerization is a prerequisite for deploying anything; missing entirely
3. Spring Boot 3.2+ enhancements — virtual threads and RestClient are high search-frequency topics that require opinionated, correct guidance
