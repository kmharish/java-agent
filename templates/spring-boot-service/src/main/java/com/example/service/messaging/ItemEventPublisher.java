package com.example.service.messaging;

import com.example.service.messaging.event.ItemCreatedEvent;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ItemEventPublisher {

    private static final Logger log = LoggerFactory.getLogger(ItemEventPublisher.class);
    private static final String TOPIC = "items.created";

    private final KafkaTemplate<String, ItemCreatedEvent> kafkaTemplate;

    public void publish(ItemCreatedEvent event) {
        kafkaTemplate.send(TOPIC, event.eventId(), event)
                .thenAccept(result -> log.debug(
                        "Published ItemCreatedEvent id={} to {}-{}@{}",
                        event.eventId(),
                        result.getRecordMetadata().topic(),
                        result.getRecordMetadata().partition(),
                        result.getRecordMetadata().offset()))
                .exceptionally(ex -> {
                    log.error("Failed to publish ItemCreatedEvent id={}", event.eventId(), ex);
                    // TODO: implement outbox pattern or dead-letter fallback for guaranteed delivery
                    return null;
                });
    }
}
