package com.example.service.config;

import com.example.service.messaging.event.ItemCreatedEvent;
import org.apache.kafka.common.TopicPartition;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.ContainerProperties;
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer;
import org.springframework.kafka.listener.DefaultErrorHandler;
import org.springframework.kafka.support.serializer.DeserializationException;
import org.springframework.util.backoff.FixedBackOff;

@Configuration
@EnableKafka
public class KafkaConfig {

    // Retry 3 times with 1s backoff, then route to <topic>.DLT
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, ItemCreatedEvent> kafkaListenerContainerFactory(
            ConsumerFactory<String, ItemCreatedEvent> consumerFactory,
            KafkaTemplate<String, ItemCreatedEvent> kafkaTemplate) {

        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(
                kafkaTemplate,
                (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition()));

        DefaultErrorHandler errorHandler = new DefaultErrorHandler(
                recoverer,
                new FixedBackOff(1_000L, 3L));  // 3 retries, 1s apart

        // Deserialization errors can never succeed on retry — skip straight to DLT
        errorHandler.addNotRetryableExceptions(DeserializationException.class);

        ConcurrentKafkaListenerContainerFactory<String, ItemCreatedEvent> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.setCommonErrorHandler(errorHandler);
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        return factory;
    }
}
