# 🏛️ System Architecture

Detailed architecture documentation for the AI Document QA System.

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                     (React + TypeScript)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ File Upload  │  │Document List │  │Chat Interface│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬───────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Upload API    │  │  Chat API    │  │Document API  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│  ┌──────▼──────────────────▼──────────────────▼───────┐        │
│  │           Document Processor Service                │        │
│  │  • Parse documents  • Chunk text  • Generate IDs   │        │
│  └──────┬─────────────────┬────────────────────┬──────┘        │
└─────────┼─────────────────┼────────────────────┼───────────────┘
          │                 │                    │
          │                 │                    │
  ┌───────▼────────┐ ┌─────▼──────┐    ┌───────▼────────┐
  │   Embeddings   │ │    LLM     │    │  Vector Store  │
  │    Service     │ │  Service   │    │    Service     │
  │                │ │            │    │                │
  │ • Generate     │ │ • Generate │    │ • Store vectors│
  │   embeddings   │ │   answers  │    │ • Search       │
  │ • Batch        │ │ • Stream   │    │ • Manage docs  │
  │   processing   │ │   responses│    │                │
  └───────┬────────┘ └─────┬──────┘    └───────┬────────┘
          │                 │                    │
          ▼                 ▼                    ▼
  ┌───────────────┐ ┌──────────────┐   ┌───────────────┐
  │    Ollama     │ │   Ollama     │   │    Qdrant     │
  │  (Embeddings) │ │    (LLM)     │   │  (Vector DB)  │
  │               │ │              │   │               │
  │ nomic-embed   │ │   llama2     │   │ • Collections │
  │    -text      │ │   mistral    │   │ • Vectors     │
  │               │ │   etc.       │   │ • Metadata    │
  └───────────────┘ └──────────────┘   └───────────────┘
```

## Component Details

### Frontend (React)

**Technology**: React 18 + TypeScript + Tailwind CSS

**Components**:
- `App.tsx` - Main application container
- `FileUpload.tsx` - Drag-and-drop file upload
- `DocumentList.tsx` - List of uploaded documents
- `ChatInterface.tsx` - Chat UI with streaming
- `MessageBubble.tsx` - Individual message display

**Services**:
- `api.ts` - API client with axios and fetch

**Features**:
- Real-time streaming responses
- Professional UI/UX
- Responsive design
- Error handling

### Backend (FastAPI)

**Technology**: Python 3.11 + FastAPI + Async/Await

**API Routes**:
- `POST /api/upload` - Upload documents
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/chat` - Ask questions (streaming/non-streaming)
- `GET /health` - Health check

**Services**:

1. **DocumentProcessor**
   - Orchestrates the RAG pipeline
   - Handles end-to-end document processing
   - Coordinates between parsers, chunker, embeddings, and vector store

2. **VectorStoreService**
   - Manages Qdrant vector database
   - Stores and retrieves embeddings
   - Performs similarity search
   - Handles document deletion

3. **EmbeddingService**
   - Generates embeddings via Ollama
   - Batch processing for efficiency
   - Async operations

4. **LLMService**
   - Generates answers using Ollama
   - Streaming and non-streaming responses
   - Context injection and prompt engineering

**Utilities**:

1. **DocumentParser**
   - Multi-format support (9 formats)
   - Extracts text from various document types
   - Preserves metadata

2. **TextChunker**
   - Smart text splitting
   - Overlap for context preservation
   - Configurable chunk size

## Data Flow

### Upload Flow

```
1. User uploads file
   ↓
2. Frontend sends to /api/upload
   ↓
3. Backend receives file
   ↓
4. DocumentParser extracts text
   ↓
5. TextChunker splits into chunks
   ↓
6. EmbeddingService generates embeddings (batch)
   ↓
7. VectorStoreService stores in Qdrant
   ↓
8. Response sent to frontend
```

### Query Flow (RAG)

```
1. User asks question
   ↓
2. Frontend sends to /api/chat
   ↓
3. EmbeddingService generates query embedding
   ↓
4. VectorStoreService searches for similar chunks
   ↓
5. Top-K relevant chunks retrieved
   ↓
6. LLMService builds context from chunks
   ↓
7. LLMService generates answer (streaming)
   ↓
8. Response streamed to frontend
   ↓
9. Frontend displays answer + sources
```

## Database Schema

### Qdrant Collection: "documents"

**Vector Configuration**:
- Size: 768 (embedding dimensions)
- Distance: Cosine similarity

**Point Payload**:
```json
{
  "text": "chunk content...",
  "document_id": "uuid",
  "chunk_id": 0,
  "filename": "document.pdf",
  "file_type": ".pdf",
  "size": 123456,
  "uploaded_at": "2024-01-01T00:00:00"
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| QDRANT_HOST | qdrant | Qdrant hostname |
| QDRANT_PORT | 6333 | Qdrant port |
| OLLAMA_HOST | ollama | Ollama hostname |
| OLLAMA_PORT | 11434 | Ollama port |
| EMBEDDING_MODEL | nomic-embed-text | Embedding model |
| LLM_MODEL | llama2 | Language model |
| CHUNK_SIZE | 1000 | Characters per chunk |
| CHUNK_OVERLAP | 200 | Overlap characters |
| CORS_ORIGINS | localhost:3000 | Allowed origins |

## Performance Characteristics

### Upload Performance

- **PDF (1MB)**: ~10-15 seconds
  - Parsing: 1-2s
  - Chunking: <1s
  - Embedding generation: 5-10s
  - Vector storage: 1-2s

- **DOCX (500KB)**: ~5-8 seconds

### Query Performance

- **Query embedding**: ~1-2 seconds
- **Vector search**: <100ms
- **LLM generation**: 3-10 seconds (depending on answer length)
- **Total**: ~5-15 seconds

### Optimization Strategies

1. **Batch Embedding**: Process multiple chunks concurrently
2. **Streaming Responses**: Start showing results immediately
3. **Connection Pooling**: Reuse connections to Qdrant
4. **Async Operations**: Non-blocking I/O throughout

## Scalability Considerations

### Current Capacity

- **Documents**: ~1000s of documents
- **Concurrent Users**: ~10-50
- **Vector Storage**: Limited by disk space

### Scaling Options

1. **Horizontal Scaling**:
   - Multiple backend instances behind load balancer
   - Shared Qdrant cluster

2. **Vertical Scaling**:
   - More RAM for larger models
   - GPU for faster inference

3. **Database Scaling**:
   - Qdrant Cloud for managed scaling
   - Sharding for large collections

## Security Architecture

### Current Security

- ✅ CORS protection
- ✅ File type validation
- ✅ Docker network isolation
- ⚠️ No authentication (development mode)

### Production Security Checklist

- [ ] Add JWT authentication
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] HTTPS/TLS
- [ ] API key management
- [ ] User isolation
- [ ] Audit logging

## Monitoring & Logging

### Logging

All services log to stdout:
- Request/response logging
- Error tracking
- Performance metrics

View with: `docker-compose logs -f`

### Health Checks

- Backend: http://localhost:8000/health
- Qdrant: http://localhost:6333/health
- Ollama: http://localhost:11434/api/tags

### Metrics to Monitor

- API response times
- Embedding generation time
- Vector search latency
- LLM inference time
- Memory usage
- Disk usage

## Technology Decisions

### Why FastAPI?
- Modern async Python framework
- Automatic API documentation
- High performance
- Type safety with Pydantic

### Why Qdrant?
- Purpose-built for vectors
- Fast similarity search
- Easy to deploy
- Good Python client

### Why Ollama?
- Local LLM execution
- Privacy-focused
- Easy model management
- No API costs

### Why React?
- Component-based architecture
- Rich ecosystem
- TypeScript support
- Good developer experience

## Future Enhancements

### Potential Features

1. **Multi-user Support**
   - User authentication
   - Document privacy
   - Shared documents

2. **Advanced RAG**
   - Re-ranking
   - Hybrid search
   - Query expansion

3. **Enhanced UI**
   - Dark mode
   - Conversation history
   - Document preview

4. **Analytics**
   - Usage statistics
   - Query analytics
   - Performance dashboards

5. **Integrations**
   - Cloud storage (S3, Drive)
   - Webhooks
   - REST API expansions

## Troubleshooting Guide

### Common Issues

1. **Services not starting**: Check Docker logs
2. **Out of memory**: Reduce chunk size or use smaller models
3. **Slow responses**: Check GPU availability, use smaller models
4. **Connection errors**: Verify Docker network

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## References

- FastAPI: https://fastapi.tiangolo.com/
- Qdrant: https://qdrant.tech/
- Ollama: https://ollama.ai/
- React: https://react.dev/
