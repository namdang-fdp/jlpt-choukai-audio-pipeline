package com.namdang.choukai.dto;

public record PresignResponse(String uploadUrl, String objectKey, long expiredAt) {}
