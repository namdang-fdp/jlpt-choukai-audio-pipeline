package com.namdang.choukai.gateway.service;

import com.namdang.choukai.gateway.dto.AudioEvent;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class KafkaProducerService {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private static final String TOPIC = "audio_uploaded";

    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    public KafkaProducerService(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public String processAndSend(String objectKey) {
        // Generate 1 cái Task ID cho Worker quản lý tiến độ
        String taskId = UUID.randomUUID().toString();

        // Đường dẫn S3 chuẩn (s3://bucket-name/object-key) để Python Worker dùng Boto3 tải về
        String realS3Url = "s3://" + bucketName + "/" + objectKey;

        AudioEvent event = new AudioEvent(taskId, realS3Url);

        kafkaTemplate.send(TOPIC, taskId, event);
        System.out.println("[Producer] Đã gửi event vào Kafka: " + event);

        return taskId;
    }
}
