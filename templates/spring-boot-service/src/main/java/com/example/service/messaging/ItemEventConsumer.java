package com.example.service.messaging;

import com.example.service.messaging.event.ItemCreatedEvent;
import lombok.RequiredArgsConstructor;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

// Stub consumer — demonstrates the pattern.
// Replace the log statement with real processing logic.
@Component
@RequiredArgsConstructor
public class ItemEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(ItemEventConsumer.class);

    @KafkaListener(
            topics = "items.created",
            groupId = "${spring.application.name}-consumer",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void consume(
            ConsumerRecord<String, ItemCreatedEvent> record,
            Acknowledgment ack) {
        try {
            ItemCreatedEvent event = record.value();
            log.info("Received ItemCreatedEvent id={} itemId={}", event.eventId(), event.itemId());

            // TODO: implement processing logic here

            ack.acknowledge();  // commit offset only after successful processing
        } catch (Exception e) {
            log.error("Failed to process record key={}", record.key(), e);
            // Do NOT ack — DefaultErrorHandler will retry, then route to DLT
            throw e;
        }
    }
}
