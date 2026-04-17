package com.namdang.choukai.service;

import com.amazonaws.HttpMethod;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.Headers;
import com.amazonaws.services.s3.model.GeneratePresignedUrlRequest;
import com.namdang.choukai.dto.PresignRequest;
import com.namdang.choukai.dto.PresignResponse;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URL;
import java.util.Date;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class S3Service {

    private final AmazonS3 amazonS3;

    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    @Value("${aws.s3.presigned-url-expiration:3600}")
    private long expiration;

    public PresignResponse generateUploadUrl(PresignRequest request) {
        // File path: choukai/{uuid}-{filename}
        String objectKey = "choukai/" + UUID.randomUUID() + "-" + request.fileName();
        Date expDate = new Date(System.currentTimeMillis() + expiration * 1000L);

        GeneratePresignedUrlRequest presignRequest =
                new GeneratePresignedUrlRequest(bucketName, objectKey)
                        .withMethod(HttpMethod.PUT)
                        .withExpiration(expDate);

        if (request.contentType() != null) {
            presignRequest.addRequestParameter(Headers.CONTENT_TYPE, request.contentType());
        }

        URL url = amazonS3.generatePresignedUrl(presignRequest);
        log.info("Generated Presigned URL for key: {}", objectKey);

        return new PresignResponse(url.toString(), objectKey, expDate.getTime());
    }
}
