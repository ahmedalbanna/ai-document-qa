# 📡 API Integration Guide

How to integrate the AI Document QA API into your applications.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (add for production).

## Endpoints

### 1. Upload Document

**Endpoint**: `POST /api/upload`

**Description**: Upload and process a document

**Content-Type**: `multipart/form-data`

**Request**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "success": true,
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "chunks": 15,
  "characters": 12450,
  "message": "Successfully processed document.pdf"
}
```

### 2. List Documents

**Endpoint**: `GET /api/documents`

**Description**: Get all uploaded documents

**Request**:
```bash
curl http://localhost:8000/api/documents
```

**Response**:
```json
[
  {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "document.pdf",
    "file_type": ".pdf",
    "size": 245678
  }
]
```

### 3. Delete Document

**Endpoint**: `DELETE /api/documents/{document_id}`

**Description**: Delete a document and all its chunks

**Request**:
```bash
curl -X DELETE http://localhost:8000/api/documents/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "success": true,
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks_deleted": 15,
  "message": "Successfully deleted document with 15 chunks"
}
```

### 4. Chat (Non-Streaming)

**Endpoint**: `POST /api/chat`

**Description**: Ask a question and get an answer

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "top_k": 5,
    "stream": false
  }'
```

**Response**:
```json
{
  "answer": "The main topic of this document is...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_id": 0,
      "score": 0.89,
      "text": "This document discusses..."
    }
  ]
}
```

### 5. Chat (Streaming)

**Endpoint**: `POST /api/chat`

**Description**: Ask a question with streaming response

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "top_k": 5,
    "stream": true
  }'
```

**Response** (Server-Sent Events):
```
data: {"type": "sources", "data": [...]}

data: {"type": "answer", "data": "The"}

data: {"type": "answer", "data": " main"}

data: {"type": "answer", "data": " topic"}

data: [DONE]
```

### 6. Health Check

**Endpoint**: `GET /health`

**Description**: Check service health

**Request**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "api": "healthy",
  "qdrant": "healthy",
  "ollama": "healthy"
}
```

## JavaScript/TypeScript Example

```typescript
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Upload document
async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_URL}/api/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data;
}

// Ask question (non-streaming)
async function askQuestion(question: string, documentId?: string) {
  const response = await axios.post(`${API_URL}/api/chat`, {
    question,
    document_id: documentId,
    top_k: 5,
    stream: false
  });
  
  return response.data;
}

// Ask question (streaming)
async function askQuestionStream(
  question: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void
) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      stream: true,
      top_k: 5
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') {
          onComplete();
          return;
        }
        
        const parsed = JSON.parse(data);
        if (parsed.type === 'answer') {
          onChunk(parsed.data);
        }
      }
    }
  }
}

// Usage
const file = document.querySelector('input[type="file"]').files[0];
const result = await uploadDocument(file);
console.log('Uploaded:', result.document_id);

const answer = await askQuestion('Summarize this document');
console.log('Answer:', answer.answer);
```

## Python Example

```python
import requests
import json

API_URL = "http://localhost:8000"

# Upload document
def upload_document(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/api/upload", files=files)
        return response.json()

# Ask question
def ask_question(question, document_id=None):
    payload = {
        'question': question,
        'document_id': document_id,
        'top_k': 5,
        'stream': False
    }
    response = requests.post(f"{API_URL}/api/chat", json=payload)
    return response.json()

# Ask question (streaming)
def ask_question_stream(question, document_id=None):
    payload = {
        'question': question,
        'document_id': document_id,
        'top_k': 5,
        'stream': True
    }
    
    with requests.post(f"{API_URL}/api/chat", json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    
                    parsed = json.loads(data)
                    if parsed['type'] == 'answer':
                        print(parsed['data'], end='', flush=True)
        print()

# Usage
result = upload_document('document.pdf')
print(f"Uploaded: {result['document_id']}")

answer = ask_question('What is this document about?')
print(f"Answer: {answer['answer']}")

# Streaming
ask_question_stream('Summarize the key points')
```

## Request Parameters

### Upload

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | Document file to upload |

### Chat

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| question | string | Yes | - | Question to ask |
| document_id | string | No | null | Filter to specific document |
| top_k | integer | No | 5 | Number of relevant chunks |
| stream | boolean | No | true | Enable streaming response |

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid file, etc.) |
| 404 | Document not found |
| 500 | Server error |
| 503 | Service unavailable |

## Rate Limits

Currently no rate limits (add for production).

## Error Handling

All errors return JSON:

```json
{
  "detail": "Error message here"
}
```

## Best Practices

1. **Check health** before making requests
2. **Handle errors** gracefully with try-catch
3. **Use streaming** for better UX
4. **Cache document IDs** to avoid re-uploading
5. **Validate files** before uploading
6. **Set timeouts** for long-running requests

## Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

## Support

For issues or questions, check the main [README.md](README.md) or open an issue.
