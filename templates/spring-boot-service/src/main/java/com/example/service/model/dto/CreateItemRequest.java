package com.example.service.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateItemRequest(
        @NotBlank(message = "name is required")
        @Size(max = 255, message = "name must be 255 characters or fewer")
        String name,

        @Size(max = 1000, message = "description must be 1000 characters or fewer")
        String description
) {}
