package com.example.service.repository;

import com.example.service.model.entity.Item;
import com.example.service.model.entity.ItemStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ItemRepository extends JpaRepository<Item, Long> {

    List<Item> findByStatus(ItemStatus status);

    boolean existsByName(String name);
}
