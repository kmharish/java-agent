package com.example.service.model.dto;

import com.example.service.model.entity.Item;
import com.example.service.model.entity.ItemStatus;

import java.time.Instant;

// Never return JPA entities directly from controllers — use DTOs.
// This record is the response shape; it decouples the API contract from the DB schema.
public record ItemDTO(
        Long id,
        String name,
        String description,
        ItemStatus status,
        Instant createdAt
) {
    public static ItemDTO from(Item item) {
        return new ItemDTO(
                item.getId(),
                item.getName(),
                item.getDescription(),
                item.getStatus(),
                item.getCreatedAt()
        );
    }
}
