# AI Document QA System - Developer Guide

## Project Overview

**AI Document QA System** is a Retrieval-Augmented Generation (RAG) application that allows users to upload documents and ask questions about them using local AI models. The system uses **Ollama** for LLM inference, **Qdrant** for vector storage, **FastAPI** for the backend, and **React** for the frontend.

### Key Features
- 📄 **Multi-format document support**: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, JSON
- 🤖 **Local LLM**: Ollama with llama2 and nomic-embed-text models
- 🗄️ **Vector database**: Qdrant for semantic search and retrieval
- 🚀 **GPU acceleration**: NVIDIA CUDA support for faster inference
- 🐳 **Fully containerized**: Docker Compose for easy deployment
- ⚡ **Real-time chat**: Streaming responses with source citations

### Tech Stack
- **Backend**: Python 3.11, FastAPI 0.109.0, async/await
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **LLM**: Ollama (local inference, no API keys)
- **Vector DB**: Qdrant 1.7.0
- **Infrastructure**: Docker, Docker Compose, NVIDIA GPU support
- **Document Processing**: PyPDF2, python-docx, pandas, beautifulsoup4

---

## Project Structure

```
.
├── backend/                      # FastAPI backend
│   ├── main.py                  # Application entry point, CORS setup
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Backend container config
│   ├── api/                     # API route handlers
│   │   ├── upload.py           # Document upload endpoint
│   │   ├── chat.py             # Question answering endpoint
│   │   └── documents.py        # Document management endpoints
│   ├── services/               # Core business logic
│   │   ├── vector_store.py     # Qdrant integration
│   │   ├── llm.py              # Ollama LLM integration
│   │   ├── embeddings.py       # Text embedding generation
│   │   └── document_processor.py # Document parsing & chunking
│   └── utils/                  # Utility functions
│       ├── parsers.py          # Document format parsers
│       └── chunking.py         # Text chunking strategies
│
├── frontend/                     # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── index.tsx           # React entry point
│   │   ├── index.css           # Global styles (Tailwind)
│   │   ├── services/
│   │   │   └── api.ts          # API client service
│   │   └── components/         # React components
│   │       ├── FileUpload.tsx   # File upload interface
│   │       ├── DocumentList.tsx # Document management UI
│   │       ├── ChatInterface.tsx # Q&A chat interface
│   │       └── MessageBubble.tsx # Chat message styling
│   ├── public/                 # Static assets
│   ├── package.json            # npm dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── tailwind.config.js      # Tailwind CSS config
│   ├── Dockerfile              # Frontend container (multi-stage)
│   └── nginx.conf              # Nginx production config
│
├── docker-compose.yml           # Full stack orchestration
├── .env                         # Environment configuration
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── startup.sh                   # Service startup script
│
├── Documentation files:
├── README.md                    # Main project documentation
├── SETUP.md                     # Setup and installation guide
├── QUICK_START.md               # Quick reference guide
├── API_GUIDE.md                 # API endpoint documentation
├── ARCHITECTURE.md              # System architecture details
├── TROUBLESHOOTING.md          # Common issues and fixes
└── CHECKLIST.md                # Pre-deployment checklist
```

---

## Environment Variables

Configure these in `.env` file before starting services:

### Qdrant Configuration
```
QDRANT_HOST=qdrant              # Vector DB hostname
QDRANT_PORT=6333               # Vector DB HTTP port
```

### Ollama Configuration
```
OLLAMA_HOST=ollama              # LLM service hostname
OLLAMA_PORT=11434              # LLM service port
EMBEDDING_MODEL=nomic-embed-text # Embedding model name
LLM_MODEL=llama2                # Main LLM model name
```

### RAG Configuration
```
CHUNK_SIZE=500                  # Document chunk size in characters
CHUNK_OVERLAP=100               # Overlap between chunks
```

### API Configuration
```
CORS_ORIGINS=https://example.com,http://localhost:3000  # CORS allowed origins
REACT_APP_API_URL=https://api.example.com               # Frontend API URL
```

---

## Development Setup

### Prerequisites
- Docker & Docker Compose v2.0+
- NVIDIA GPU (optional, for GPU acceleration)
- Python 3.11+ (for local development)
- Node.js 18+ (for local frontend development)

### Quick Start

1. **Clone and setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services**
   ```bash
   docker compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Qdrant Dashboard: http://localhost:6333/dashboard

4. **Stop services**
   ```bash
   docker compose down
   ```

### Local Development (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
QDRANT_HOST=localhost OLLAMA_HOST=localhost uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## API Endpoints

### File Upload
```
POST /api/upload
- Accepts: multipart/form-data with file
- Returns: { document_id, filename, chunks, characters }
- Supported types: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, JSON
```

### List Documents
```
GET /api/documents
- Returns: List of uploaded documents with metadata
```

### Delete Document
```
DELETE /api/documents/{document_id}
- Removes document and its embeddings from vector store
```

### Ask Question
```
POST /api/ask
- Body: { question: string, document_id?: string }
- Returns: StreamingResponse with chunks containing { answer, sources }
```

### Health Check
```
GET /health
- Returns: Status of API, Qdrant, and Ollama services
```

---

## Key Components & Services

### Backend Services

#### VectorStoreService (services/vector_store.py)
- Manages Qdrant client connections
- Handles document insertion and retrieval
- Performs semantic similarity search
- **Key methods**: `insert_embeddings()`, `search()`, `health_check()`

#### LLMService (services/llm.py)
- Wraps Ollama API client
- Manages model inference with streaming
- Handles context window and token limits
- **Key methods**: `generate()`, `chat()`, `health_check()`

#### EmbeddingService (services/embeddings.py)
- Generates text embeddings using Ollama
- Handles batch embedding operations
- Caches embeddings for efficiency
- **Key methods**: `embed()`, `embed_batch()`

#### DocumentProcessor (services/document_processor.py)
- Orchestrates document parsing and chunking
- Coordinates embedding generation and storage
- Tracks document metadata
- **Key methods**: `process_document()`, `delete_document()`

### Frontend Components

#### FileUpload
- Drag-and-drop or click-to-upload interface
- File validation and progress tracking
- Success/error notifications

#### DocumentList
- Lists all uploaded documents
- Provides document selection and deletion
- Shows document metadata

#### ChatInterface
- Chat message input and display
- Streaming response handling
- Source citation display
- Empty state management

#### MessageBubble
- User and AI message styling
- Code block rendering
- Source link formatting

---

## Important Development Practices

### Document Processing Flow

1. **Upload** → File received, validated
2. **Parse** → Extract text from document format
3. **Chunk** → Split into overlapping segments (500 chars, 100 overlap)
4. **Embed** → Generate embeddings using nomic-embed-text
5. **Store** → Insert embeddings into Qdrant
6. **Index** → Make searchable for retrieval

### RAG Question Answering Flow

1. **Retrieve** → Semantic search in vector store
2. **Rank** → Sort results by relevance
3. **Context** → Build prompt with top results
4. **Generate** → LLM produces answer with streaming
5. **Return** → Stream answer chunks with sources

### Error Handling

- **Validation errors**: 400 Bad Request with clear message
- **Service unavailable**: 503 Service Unavailable (check docker-compose)
- **Async errors**: Caught and logged, returned as 500 Internal Server Error
- **GPU errors**: Falls back to CPU processing automatically

### Logging

Backend uses Python logging module configured in `main.py`:
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Check logs with:
```bash
docker compose logs backend -f  # Follow backend logs
docker compose logs ollama -f   # Follow Ollama logs
```

---

## Performance Optimization

### GPU Acceleration
- Ollama is configured with NVIDIA GPU support
- Check GPU usage: `nvidia-smi`
- Fallback to CPU if GPU unavailable
- Monitor inference latency in logs

### Vector Store Optimization
- Qdrant uses hierarchical navigation structures
- Document chunking reduces search space
- Batch operations for bulk inserts
- Regular indexing for performance

### Frontend Performance
- React.lazy() for code splitting
- CSS-in-JS (Tailwind) for minimal bundle
- Debounced search queries
- Streaming response rendering

---

## Testing & Debugging

### API Testing
```bash
# Test health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/api/documents

# Upload document
curl -F "file=@document.pdf" http://localhost:8000/api/upload

# Ask question (streaming)
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is RAG?"}'
```

### Browser DevTools
- Check Network tab for API calls
- Console logs for frontend errors
- React DevTools for component inspection
- Check CORS errors if frontend can't reach backend

### Docker Debugging
```bash
# Enter container shell
docker exec -it ai-qa-backend bash

# Check service connectivity
docker exec ai-qa-backend curl http://ollama:11434/api/tags
docker exec ai-qa-backend curl http://qdrant:6333/health

# View container logs
docker compose logs [service-name]
```

---

## Common Issues & Solutions

### "Failed to load documents" Error
- **Cause**: Frontend can't reach backend API
- **Fix**: Check CORS_ORIGINS and REACT_APP_API_URL in .env
- **Check**: `curl http://localhost:8000/api/documents`

### "Input length exceeds context length" Error
- **Cause**: Document chunks too large for embedding model
- **Fix**: Reduce CHUNK_SIZE in .env (try 300-400)
- **Note**: Already fixed in current config (CHUNK_SIZE=500)

### GPU Not Detected
- **Cause**: NVIDIA drivers not installed or Docker missing GPU config
- **Fix**: Verify `nvidia-smi` works, check docker-compose.yml GPU section
- **Fallback**: System will use CPU (slower but functional)

### Services Not Starting
- **Cause**: Port conflicts or insufficient disk space
- **Fix**: Check `docker compose ps`, verify ports 3000, 6333, 8000, 11434 are free
- **Reset**: `docker compose down -v` to remove volumes and start fresh

### Models Not Downloading
- **Cause**: Network issues or insufficient storage
- **Fix**: Run manually: `docker exec ai-qa-ollama ollama pull llama2`
- **Monitor**: Check docker compose logs for progress

---

## Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   export REACT_APP_API_URL=https://api.yourdomain.com
   export CORS_ORIGINS=https://yourdomain.com
   ```

2. **Build Images**
   ```bash
   docker compose build
   ```

3. **Start Services**
   ```bash
   docker compose up -d
   ```

4. **Health Check**
   ```bash
   curl https://yourdomain.com/health
   ```

### Scaling Considerations
- **Horizontal**: Run multiple API instances behind load balancer
- **Vertical**: Increase CHUNK_SIZE for more context per query
- **Storage**: Use cloud storage for document persistence
- **Cache**: Implement Redis for embedding caching

---

## Contributing Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: ESLint configuration in place, use strict mode
- **Comments**: Document complex logic, explain "why" not "what"

### Git Workflow
1. Create feature branch from main
2. Make changes with clear commit messages
3. Test locally before pushing
4. Submit PR with description of changes
5. Address review feedback

### Testing
- Unit tests for parsers and chunking
- Integration tests for API endpoints
- Manual testing with various document types
- Performance testing with large documents

### Documentation
- Update README.md for feature changes
- Add docstrings to new functions
- Update API_GUIDE.md for new endpoints
- Record any breaking changes

---

## Support & Resources

### Documentation Files
- `README.md` - Project overview and quick setup
- `API_GUIDE.md` - Detailed API endpoint reference
- `ARCHITECTURE.md` - System design and data flow
- `TROUBLESHOOTING.md` - Common issues and solutions
- `SETUP.md` - Detailed installation guide

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [React Documentation](https://react.dev/)

### Key Concepts
- **RAG**: Retrieval-Augmented Generation for accurate AI responses
- **Vector Embeddings**: Semantic representations for similarity search
- **Chunking**: Breaking documents into manageable segments
- **CORS**: Cross-Origin Resource Sharing for frontend-backend communication

---

## Quick Commands Reference

```bash
# Development
docker compose up -d                          # Start all services
docker compose down                           # Stop all services
docker compose logs -f backend                # View backend logs
docker compose ps                             # Show service status

# Testing
curl http://localhost:8000/health            # Health check
curl http://localhost:8000/docs              # Swagger UI
docker exec ai-qa-ollama ollama list         # List available models

# Debugging
docker exec -it ai-qa-backend bash           # Backend shell
docker exec -it ai-qa-frontend bash          # Frontend shell
docker compose exec qdrant curl http://localhost:6333/health

# Cleanup
docker compose down -v                        # Remove volumes
docker system prune                           # Remove unused containers/images
```

---

**Last Updated**: February 21, 2026  
**Version**: 1.0.0  
**Status**: Production Ready with GPU Support
