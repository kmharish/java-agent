package com.example.service.service;

import com.example.service.exception.ItemNotFoundException;
import com.example.service.messaging.ItemEventPublisher;
import com.example.service.messaging.event.ItemCreatedEvent;
import com.example.service.model.dto.CreateItemRequest;
import com.example.service.model.dto.ItemDTO;
import com.example.service.model.entity.Item;
import com.example.service.model.entity.ItemStatus;
import com.example.service.repository.ItemRepository;
import io.micrometer.core.annotation.Timed;
import io.micrometer.core.instrument.MeterRegistry;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ItemService {

    private static final Logger log = LoggerFactory.getLogger(ItemService.class);

    private final ItemRepository itemRepository;
    private final ItemEventPublisher eventPublisher;
    private final MeterRegistry meterRegistry;

    @Timed(value = "items.find_all", description = "Time to fetch all active items")
    @Transactional(readOnly = true)
    public List<ItemDTO> findAll() {
        return itemRepository.findByStatus(ItemStatus.ACTIVE).stream()
                .map(ItemDTO::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public ItemDTO findById(Long id) {
        return itemRepository.findById(id)
                .map(ItemDTO::from)
                .orElseThrow(() -> new ItemNotFoundException(id));
    }

    @Timed(value = "items.create", description = "Time to create an item")
    @Transactional
    public ItemDTO create(CreateItemRequest request) {
        Item item = new Item();
        item.setName(request.name());
        item.setDescription(request.description());

        Item saved = itemRepository.save(item);
        log.info("Created item id={} name={}", saved.getId(), saved.getName());

        meterRegistry.counter("items.created").increment();
        eventPublisher.publish(new ItemCreatedEvent(saved.getId(), saved.getName()));

        return ItemDTO.from(saved);
    }

    @Transactional
    public void delete(Long id) {
        Item item = itemRepository.findById(id)
                .orElseThrow(() -> new ItemNotFoundException(id));
        item.setStatus(ItemStatus.DELETED);  // soft delete
        log.info("Soft-deleted item id={}", id);
    }
}
