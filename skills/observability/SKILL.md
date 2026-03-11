---
name: observability
description: Spring Boot Actuator, Micrometer metrics, OpenTelemetry tracing, structured logging, and production monitoring patterns
tools: [bash, read_file, write_file, edit_file]
---

# Observability Skill

Production Java services need three pillars: **metrics**, **traces**, and **logs**. This skill covers all three with Spring Boot 3.x patterns.

## Dependencies

```xml
<!-- Spring Boot Actuator -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>

<!-- Micrometer with Prometheus registry -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>

<!-- OpenTelemetry tracing (Spring Boot 3.x uses Micrometer Tracing) -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>

<!-- Zipkin alternative (lighter, no collector needed for dev) -->
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
```

## Spring Boot Actuator Configuration

### application.yml
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus, loggers, env
      base-path: /actuator
  endpoint:
    health:
      show-details: when-authorized  # never | always | when-authorized
      probes:
        enabled: true  # liveness + readiness for K8s
    prometheus:
      enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: ${spring.application.name}
      environment: ${spring.profiles.active:default}
  tracing:
    sampling:
      probability: 1.0  # 100% in dev; use 0.1 in prod
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
```

### Security: Lock down actuator endpoints
```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
        return http
            .securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(EndpointRequest.to(HealthEndpoint.class)).permitAll()
                .requestMatchers(EndpointRequest.to(InfoEndpoint.class)).permitAll()
                .anyRequest().hasRole("ACTUATOR_ADMIN")
            )
            .httpBasic(Customizer.withDefaults())
            .build();
    }
}
```

## Micrometer Metrics

### Counter — track events
```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final MeterRegistry registry;

    // Prefer method-level registration over constructor to avoid startup cost
    public void placeOrder(Order order) {
        // ... business logic ...
        registry.counter("orders.placed",
            "status", "success",
            "region", order.getRegion()
        ).increment();
    }

    public void failOrder(Order order, String reason) {
        registry.counter("orders.failed",
            "reason", reason
        ).increment();
    }
}
```

### Timer — measure latency
```java
@Service
@RequiredArgsConstructor
public class PaymentService {
    private final MeterRegistry registry;

    public PaymentResult process(PaymentRequest request) {
        return Timer.builder("payment.processing")
            .tag("provider", request.getProvider())
            .description("Time to process a payment")
            .register(registry)
            .record(() -> doProcess(request));
    }
}
```

### Gauge — track current state
```java
@Configuration
public class MetricsConfig {

    @Bean
    public MeterBinder queueMetrics(Queue<Order> orderQueue) {
        return registry -> Gauge.builder("order.queue.size", orderQueue, Queue::size)
            .description("Current number of orders in queue")
            .register(registry);
    }
}
```

### @Timed annotation (AOP-based, less overhead in code)
```java
// Requires TimedAspect bean
@Configuration
public class MicrometerConfig {
    @Bean
    public TimedAspect timedAspect(MeterRegistry registry) {
        return new TimedAspect(registry);
    }
}

@Service
public class InventoryService {

    @Timed(value = "inventory.check", description = "Time to check inventory", percentiles = {0.5, 0.95, 0.99})
    public boolean isAvailable(String sku) {
        // ...
    }
}
```

### Custom Health Indicator
```java
@Component
public class ExternalApiHealthIndicator implements HealthIndicator {
    private final ExternalApiClient client;

    @Override
    public Health health() {
        try {
            var status = client.ping();
            return Health.up()
                .withDetail("response_time_ms", status.latency())
                .withDetail("version", status.version())
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

## OpenTelemetry Distributed Tracing

### Automatic propagation
Spring Boot 3.x with Micrometer Tracing handles `traceparent` / `traceId` / `spanId` propagation automatically for:
- Incoming HTTP requests (via filter)
- `RestTemplate` / `WebClient` / `FeignClient` outbound calls
- `@Async` methods
- Kafka/RabbitMQ messages (with instrumentation)

### Manual span creation
```java
@Service
@RequiredArgsConstructor
public class ShipmentService {
    private final Tracer tracer;  // io.micrometer.tracing.Tracer

    public ShipmentResult ship(Order order) {
        Span span = tracer.nextSpan()
            .name("shipment.create")
            .tag("order.id", order.getId())
            .tag("carrier", order.getCarrier())
            .start();

        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            return doShip(order);
        } catch (Exception e) {
            span.error(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

### Propagate trace context to async operations
```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(8);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        // Wrap with context propagation so traceId flows into async threads
        executor.setTaskDecorator(new ContextPropagatingTaskDecorator());
        executor.initialize();
        return executor;
    }
}
```

## Structured Logging with Trace Correlation

### logback-spring.xml with JSON output (production)
```xml
<configuration>
    <springProfile name="prod">
        <appender name="JSON_STDOUT" class="ch.qos.logback.core.ConsoleAppender">
            <encoder class="net.logstash.logback.encoder.LogstashEncoder">
                <!-- traceId/spanId are auto-added by Micrometer Tracing via MDC -->
                <includeMdcKeyName>traceId</includeMdcKeyName>
                <includeMdcKeyName>spanId</includeMdcKeyName>
                <includeMdcKeyName>userId</includeMdcKeyName>
            </encoder>
        </appender>
        <root level="INFO">
            <appender-ref ref="JSON_STDOUT"/>
        </root>
    </springProfile>

    <springProfile name="!prod">
        <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
            <encoder>
                <!-- Include traceId in human-readable format for dev -->
                <pattern>%d{HH:mm:ss} [%thread] [%X{traceId}] %-5level %logger{36} - %msg%n</pattern>
            </encoder>
        </appender>
        <root level="DEBUG">
            <appender-ref ref="CONSOLE"/>
        </root>
    </springProfile>
</configuration>
```

### Add business context to MDC
```java
@RestController
@RequiredArgsConstructor
public class OrderController {

    @PostMapping("/orders")
    public ResponseEntity<OrderDTO> create(@Valid @RequestBody CreateOrderRequest req,
                                           @AuthenticationPrincipal UserDetails user) {
        // Add business context — will appear in all log lines for this request
        MDC.put("userId", user.getUsername());
        MDC.put("orderId", UUID.randomUUID().toString());
        try {
            return ResponseEntity.status(HttpStatus.CREATED)
                .body(orderService.create(req));
        } finally {
            MDC.remove("userId");
            MDC.remove("orderId");
        }
    }
}
```

### MDC via filter (preferred for web requests)
```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestContextFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String requestId = Optional.ofNullable(request.getHeader("X-Request-ID"))
            .orElse(UUID.randomUUID().toString());
        MDC.put("requestId", requestId);
        response.setHeader("X-Request-ID", requestId);
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.clear();
        }
    }
}
```

## Production Monitoring Patterns

### Info endpoint — expose build metadata
```xml
<!-- pom.xml: enable build-info generation -->
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals>
                <goal>build-info</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

```yaml
# application.yml
info:
  app:
    name: ${spring.application.name}
    version: @project.version@
  git:
    commit: @git.commit.id.abbrev@  # requires git-commit-id-plugin
```

### Graceful shutdown with readiness probe
```yaml
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # wait for in-flight requests

server:
  shutdown: graceful

management:
  endpoint:
    health:
      probes:
        enabled: true
# Kubernetes: liveness = /actuator/health/liveness, readiness = /actuator/health/readiness
```

### Key metrics to alert on
| Metric | Prometheus Query | Alert Threshold |
|--------|-----------------|-----------------|
| Error rate | `rate(http_server_requests_seconds_count{status=~"5.."}[5m])` | > 1% of requests |
| p99 latency | `histogram_quantile(0.99, http_server_requests_seconds_bucket)` | > 2s |
| JVM heap | `jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"}` | > 85% |
| GC pause time | `rate(jvm_gc_pause_seconds_sum[5m])` | > 100ms avg |
| DB pool wait | `hikaricp_connections_pending` | > 5 |
| Thread pool full | `executor_pool_size_threads - executor_active_threads` | < 2 remaining |

### Prometheus scrape config
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'spring-app'
    metrics_path: '/actuator/prometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['app:8080']
    basic_auth:
      username: actuator
      password: secret
```

## Common Pitfalls

- **Don't expose actuator on the public port in prod.** Bind to a separate management port: `management.server.port=8081` and firewall it.
- **Don't use `show-details: always` in prod.** It leaks internal topology.
- **Don't create high-cardinality tags.** Tags like `userId` or `orderId` on metrics will OOM Prometheus. Use them in traces/logs instead.
- **`@Timed` requires `TimedAspect` bean.** Without it, the annotation silently does nothing.
- **MDC.clear() in finally block.** Always clear MDC to prevent context leakage between pooled threads.
- **Sampling rate.** 100% sampling (`probability: 1.0`) is fine for dev/staging. In prod, start at 10% (`0.1`) and adjust based on volume.
