# Kafka / Spring Messaging Skill

Spring Kafka patterns for production microservices. Opinionated, battle-tested.

---

## Dependencies

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
<!-- For JSON serialization -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

---

## Producer Configuration

### String Producer (simple)

```java
@Configuration
public class KafkaProducerConfig {

    @Bean
    public ProducerFactory<String, String> producerFactory(KafkaProperties props) {
        Map<String, Object> config = new HashMap<>(props.buildProducerProperties());
        config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        // Idempotent producer: exactly-once delivery to the broker
        config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        // acks=all required for idempotency
        config.put(ProducerConfig.ACKS_CONFIG, "all");
        config.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
        config.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        return new DefaultKafkaProducerFactory<>(config);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate(ProducerFactory<String, String> pf) {
        return new KafkaTemplate<>(pf);
    }
}
```

### JSON Producer

```java
@Bean
public ProducerFactory<String, OrderEvent> jsonProducerFactory(KafkaProperties props) {
    Map<String, Object> config = new HashMap<>(props.buildProducerProperties());
    config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
    config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
    config.put(JsonSerializer.ADD_TYPE_INFO_HEADERS, false); // avoid type header coupling
    config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
    config.put(ProducerConfig.ACKS_CONFIG, "all");
    return new DefaultKafkaProducerFactory<>(config);
}

@Bean
public KafkaTemplate<String, OrderEvent> orderKafkaTemplate(
        ProducerFactory<String, OrderEvent> pf) {
    return new KafkaTemplate<>(pf);
}
```

### Transactional Producer (exactly-once semantics)

```java
@Bean
public ProducerFactory<String, OrderEvent> transactionalProducerFactory(KafkaProperties props) {
    Map<String, Object> config = new HashMap<>(props.buildProducerProperties());
    config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
    config.put(ProducerConfig.ACKS_CONFIG, "all");
    DefaultKafkaProducerFactory<String, OrderEvent> factory =
            new DefaultKafkaProducerFactory<>(config);
    factory.setTransactionIdPrefix("order-tx-");
    return factory;
}

@Bean
public KafkaTransactionManager<String, OrderEvent> kafkaTransactionManager(
        ProducerFactory<String, OrderEvent> pf) {
    return new KafkaTransactionManager<>(pf);
}
```

Usage with transactions:

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    @Transactional("kafkaTransactionManager")
    public void placeOrder(Order order) {
        // DB write + Kafka publish in one atomic unit (requires Kafka transactions)
        orderRepository.save(order);
        kafkaTemplate.send("orders", order.getId(), new OrderEvent(order));
    }
}
```

> **Note:** True exactly-once across DB + Kafka requires outbox pattern or a Kafka-only transaction boundary. `@Transactional` over both only works if you're using ChainedKafkaTransactionManager or the outbox pattern.

---

## Consumer Configuration

### String Consumer

```java
@Configuration
@EnableKafka
public class KafkaConsumerConfig {

    @Bean
    public ConsumerFactory<String, String> consumerFactory(KafkaProperties props) {
        Map<String, Object> config = new HashMap<>(props.buildConsumerProperties());
        config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        config.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        config.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        config.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false); // manual ack
        return new DefaultKafkaConsumerFactory<>(config);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
            ConsumerFactory<String, String> cf) {
        ConcurrentKafkaListenerContainerFactory<String, String> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(cf);
        factory.setConcurrency(3); // match partition count or less
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        return factory;
    }
}
```

### JSON Consumer

```java
@Bean
public ConsumerFactory<String, OrderEvent> jsonConsumerFactory(KafkaProperties props) {
    Map<String, Object> config = new HashMap<>(props.buildConsumerProperties());
    config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
    config.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
    config.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS, JsonDeserializer.class.getName());
    config.put(JsonDeserializer.TRUSTED_PACKAGES, "com.example.events");
    config.put(JsonDeserializer.VALUE_DEFAULT_TYPE, OrderEvent.class.getName());
    config.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
    config.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
    return new DefaultKafkaConsumerFactory<>(config,
            new StringDeserializer(),
            new ErrorHandlingDeserializer<>(new JsonDeserializer<>(OrderEvent.class)));
}
```

> **Always** wrap deserializers with `ErrorHandlingDeserializer` for JSON consumers. Without it, a single malformed message (poison pill) crashes the entire consumer.

---

## @KafkaListener with Explicit Acknowledgment

```java
@Component
@RequiredArgsConstructor
public class OrderEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(OrderEventConsumer.class);
    private final OrderProcessor processor;

    @KafkaListener(
        topics = "orders",
        groupId = "order-service",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void consume(
            ConsumerRecord<String, OrderEvent> record,
            Acknowledgment ack) {
        try {
            processor.process(record.value());
            ack.acknowledge(); // commit offset only on success
        } catch (RecoverableException e) {
            log.warn("Recoverable error for key={}, will retry", record.key(), e);
            // do NOT ack — container will retry based on error handler config
            throw e;
        } catch (Exception e) {
            log.error("Fatal error for key={}, sending to DLQ", record.key(), e);
            ack.acknowledge(); // ack to skip — DLQ handler already routed it
        }
    }
}
```

---

## Dead-Letter Queue (DLQ) Setup

### DefaultErrorHandler with DLQ

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory(
        ConsumerFactory<String, OrderEvent> cf,
        KafkaTemplate<String, OrderEvent> kafkaTemplate) {

    DeadLetterPublishingRecoverer recoverer =
            new DeadLetterPublishingRecoverer(kafkaTemplate,
                (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition()));

    DefaultErrorHandler errorHandler = new DefaultErrorHandler(
            recoverer,
            new FixedBackOff(1000L, 3L)); // 3 retries, 1s apart

    // Don't retry deserialization errors — they'll never succeed
    errorHandler.addNotRetryableExceptions(DeserializationException.class);

    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(cf);
    factory.setCommonErrorHandler(errorHandler);
    factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);
    return factory;
}
```

### DLQ Consumer

```java
@KafkaListener(topics = "orders.DLT", groupId = "order-dlq-processor")
public void consumeDlq(
        ConsumerRecord<String, OrderEvent> record,
        @Header(KafkaHeaders.EXCEPTION_MESSAGE) String exceptionMessage) {
    log.error("DLQ message: key={}, error={}", record.key(), exceptionMessage);
    // alert, store for manual review, etc.
}
```

---

## KafkaTemplate Usage

```java
@Service
@RequiredArgsConstructor
public class EventPublisher {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public void publish(String topic, String key, OrderEvent event) {
        kafkaTemplate.send(topic, key, event)
                .thenAccept(result -> log.debug("Sent to {}-{}@{}",
                        result.getRecordMetadata().topic(),
                        result.getRecordMetadata().partition(),
                        result.getRecordMetadata().offset()))
                .exceptionally(ex -> {
                    log.error("Failed to send event key={}", key, ex);
                    // handle: retry, fallback, outbox, etc.
                    return null;
                });
    }

    // Synchronous send (use sparingly — blocks calling thread)
    public RecordMetadata publishSync(String topic, String key, OrderEvent event)
            throws ExecutionException, InterruptedException {
        return kafkaTemplate.send(topic, key, event).get().getRecordMetadata();
    }
}
```

---

## application.yml Configuration

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      retries: 2147483647
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
    consumer:
      group-id: my-service
      auto-offset-reset: earliest
      enable-auto-commit: false
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.ErrorHandlingDeserializer
      properties:
        spring.deserializer.value.delegate.class: org.springframework.kafka.support.serializer.JsonDeserializer
        spring.json.trusted.packages: "com.example.events"
    listener:
      ack-mode: manual_immediate
      concurrency: 3
```

---

## Testing

### @EmbeddedKafka (fast, unit-level)

```java
@SpringBootTest
@EmbeddedKafka(
    partitions = 1,
    topics = {"orders", "orders.DLT"},
    brokerProperties = {
        "transaction.state.log.replication.factor=1",
        "transaction.state.log.min.isr=1"
    }
)
@TestPropertySource(properties = {
    "spring.kafka.bootstrap-servers=${spring.embedded.kafka.brokers}"
})
class OrderEventConsumerTest {

    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;

    @Autowired
    private OrderProcessor orderProcessor; // spy or mock this

    @Test
    void shouldProcessOrderEvent() throws Exception {
        OrderEvent event = new OrderEvent("order-1", OrderStatus.PLACED);
        kafkaTemplate.send("orders", "order-1", event).get();

        // await processing — use Awaitility
        await().atMost(Duration.ofSeconds(10))
               .untilAsserted(() ->
                   verify(orderProcessor).process(argThat(e -> "order-1".equals(e.orderId()))));
    }
}
```

### Testcontainers Kafka (integration, closer to prod)

```java
@SpringBootTest
@Testcontainers
class OrderIntegrationTest {

    @Container
    static KafkaContainer kafka = new KafkaContainer(
            DockerImageName.parse("confluentinc/cp-kafka:7.6.0"));

    @DynamicPropertySource
    static void kafkaProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Test
    void fullRoundTrip() {
        // produce → consume → assert side effects
    }
}
```

> Use `@EmbeddedKafka` for fast feedback in unit tests. Use Testcontainers for integration tests that need real broker behavior (exactly-once, transactions, rebalancing).

---

## Common Pitfalls

### 1. Consumer Group Rebalancing
- **Problem:** Adding/removing consumers or slow processing triggers rebalances, causing duplicate processing.
- **Fix:** Keep `max.poll.interval.ms` higher than your slowest processing time. Process quickly or increase the timeout. Use idempotent consumers (deduplicate by event ID).

```yaml
spring.kafka.consumer.properties:
  max.poll.interval.ms: 300000  # 5 minutes — tune to your processing time
  max.poll.records: 50           # fewer records per poll if processing is slow
```

### 2. Poison Pills (Deserialization Failures)
- **Problem:** One malformed message blocks the entire partition forever.
- **Fix:** Always use `ErrorHandlingDeserializer`. Configure DLQ or a `DeadLetterPublishingRecoverer`.

```java
// WRONG — crashes on any bad message
config.put(VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);

// RIGHT — routes bad messages to DLT, continues processing
config.put(VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
config.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS, JsonDeserializer.class.getName());
```

### 3. Serialization Mismatches
- **Problem:** Producer uses one class, consumer expects another. `__TypeId__` header causes `ClassNotFoundException`.
- **Fix:** Disable type headers on producer (`ADD_TYPE_INFO_HEADERS=false`), set explicit type on consumer.

```java
// Producer
config.put(JsonSerializer.ADD_TYPE_INFO_HEADERS, false);

// Consumer
config.put(JsonDeserializer.VALUE_DEFAULT_TYPE, "com.example.events.OrderEvent");
```

### 4. Auto-Commit with Manual Processing
- **Problem:** `enable.auto.commit=true` commits offsets before processing completes. Messages lost on crash.
- **Fix:** Always use `enable.auto.commit=false` with `AckMode.MANUAL_IMMEDIATE` or `AckMode.RECORD`.

### 5. Missing `acks=all` on Producer
- **Problem:** Default `acks=1` means leader acknowledges but followers may not have the message. Data loss on leader failure.
- **Fix:** Set `acks=all` and `min.insync.replicas=2` on the topic.

### 6. Unhandled Exceptions Stopping the Container
- **Problem:** Uncaught exceptions in `@KafkaListener` stop the listener container in older Spring Kafka versions.
- **Fix:** Always configure a `DefaultErrorHandler` (Spring Kafka 2.8+). Don't rely on the default.

---

## Checklist

- [ ] `acks=all` + `enable.idempotence=true` on producer
- [ ] `enable.auto.commit=false` + explicit `AckMode` on consumer
- [ ] `ErrorHandlingDeserializer` wrapping JSON deserializer
- [ ] `DefaultErrorHandler` with `DeadLetterPublishingRecoverer` configured
- [ ] DLQ topic (`*.DLT`) monitored and consumed
- [ ] `max.poll.interval.ms` tuned for processing time
- [ ] Tests with `@EmbeddedKafka` or Testcontainers
- [ ] No secrets in bootstrap-servers config (use env vars or Vault)
