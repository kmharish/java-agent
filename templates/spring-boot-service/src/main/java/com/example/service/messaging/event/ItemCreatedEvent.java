package com.example.service.messaging.event;

import java.time.Instant;
import java.util.UUID;

// Immutable event record — never expose JPA entities in Kafka messages.
// Consumers depend on this contract; changing field names is a breaking change.
public record ItemCreatedEvent(
        String eventId,      // idempotency key for consumers
        Long itemId,
        String itemName,
        Instant occurredAt
) {
    public ItemCreatedEvent(Long itemId, String itemName) {
        this(UUID.randomUUID().toString(), itemId, itemName, Instant.now());
    }
}
