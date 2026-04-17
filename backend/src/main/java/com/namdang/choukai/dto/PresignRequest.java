package com.namdang.choukai.dto;

public record PresignRequest(String fileName, String contentType, Long fileSize) {}
