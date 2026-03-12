package com.example.service.controller;

import com.example.service.model.dto.CreateItemRequest;
import com.example.service.model.dto.ItemDTO;
import com.example.service.service.ItemService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/items")
@RequiredArgsConstructor
public class ItemController {

    private final ItemService itemService;

    @GetMapping
    public ResponseEntity<List<ItemDTO>> getAll() {
        return ResponseEntity.ok(itemService.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<ItemDTO> getById(@PathVariable Long id) {
        return ResponseEntity.ok(itemService.findById(id));
    }

    @PostMapping
    public ResponseEntity<ItemDTO> create(@Valid @RequestBody CreateItemRequest request) {
        ItemDTO created = itemService.create(request);
        MDC.put("itemId", String.valueOf(created.id()));  // correlate logs for this request
        try {
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } finally {
            MDC.remove("itemId");
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        itemService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
