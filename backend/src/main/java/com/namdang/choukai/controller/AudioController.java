package com.namdang.choukai.controller;

import com.namdang.choukai.dto.PresignRequest;
import com.namdang.choukai.dto.PresignResponse;
import com.namdang.choukai.gateway.service.KafkaProducerService;
import com.namdang.choukai.service.S3Service;

import lombok.RequiredArgsConstructor;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/audio")
@RequiredArgsConstructor
public class AudioController {

    private final S3Service s3Service;

    private final KafkaProducerService kafkaProducer;

    @PostMapping("/presign")
    public ResponseEntity<PresignResponse> getPresignUrl(@RequestBody PresignRequest request) {
        return ResponseEntity.ok(s3Service.generateUploadUrl(request));
    }

    @PostMapping("/confirm-upload")
    public ResponseEntity<String> confirmUpload(@RequestParam String objectKey) {
        // Trigger Kafka: FE báo đã upload xong, ném file cho Worker xử lý
        kafkaProducer.processAndSend(objectKey);
        return ResponseEntity.ok("Task bóc băng đã được đẩy vào hàng đợi Kafka!");
    }
}
