# Transcription

## Transcribe Audio
```http
POST /transcribe
```
Request (multipart/form-data):
```
audio: [audio file]
```
Response:
```json
{
    "transcript": "Therapist: How have you been feeling lately? Client: I've been feeling quite anxious...",
    "status": "completed"
}
```

## Get Transcription Status
```http
GET /transcribe/{transcription_id}
```
Response:
```json
{
    "status": "processing",
    "progress": 75
}
```

## Error Responses

- 400: Bad Request
  - Invalid file format
  - Unsupported language
  - File too large
- 401: Unauthorized
- 403: Forbidden
- 404: Transcription not found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

- 10 transcriptions per minute per user
- 100 transcriptions per hour per user
- 1GB total file size per hour per user

## Supported Audio Formats

- MP3 (.mp3)
- M4A (.m4a)
- WAV (.wav)
- MP4 (.mp4)
- MPEG (.mpeg, .mpga)
- WebM (.webm)

## Response Formats

- JSON: Structured data with timestamps and confidence scores
- Text: Plain text transcription
- SRT: SubRip subtitle format
- VTT: WebVTT subtitle format 