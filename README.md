# 🤖 AI Document QA System

A professional, high-performance **Retrieval-Augmented Generation (RAG)** system for document question-answering. Upload documents in various formats and ask questions using AI-powered semantic search and natural language understanding.

## ✨ Features

### 🚀 **Fast & Accurate**
- **RAG Pipeline**: Combines vector search with LLM generation for accurate, context-aware answers
- **Semantic Search**: Uses embeddings to find the most relevant document chunks
- **Streaming Responses**: Real-time answer generation for better user experience
- **Citation Tracking**: Shows which documents and sections were used to generate answers

### 📁 **Multi-Format Support**
Upload and process various document types:
- **Documents**: PDF, DOCX, DOC, TXT, Markdown
- **Spreadsheets**: XLSX, XLS, CSV
- **Presentations**: PPTX, PPT
- **Web & Data**: HTML, JSON

### 🛠️ **Technology Stack**
- **Backend**: FastAPI (Python) - High-performance async API
- **Vector Database**: Qdrant - Fast similarity search
- **LLM**: Ollama - Local AI models (Llama2, etc.)
- **Embeddings**: Nomic Embed Text - Quality embeddings
- **Frontend**: React + TypeScript + Tailwind CSS
- **Deployment**: Docker Compose - All-in-one setup

### 💡 **Smart Processing**
- **Intelligent Chunking**: Splits documents with overlap for better context
- **Batch Embedding**: Efficient parallel processing
- **Metadata Tracking**: Preserves document structure and references
- **Error Recovery**: Robust error handling throughout

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│   Qdrant    │
│  Frontend   │◀─────│   Backend    │◀─────│  Vector DB  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Ollama    │
                     │   LLM Engine │
                     └──────────────┘
```

### Data Flow
1. **Upload**: Document → Parser → Chunker → Embeddings → Vector DB
2. **Query**: Question → Embedding → Vector Search → Context Retrieval → LLM → Answer

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM recommended
- GPU optional (for faster inference)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-document-qa
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Pull Ollama models** (first time only)
```bash
# Pull embedding model
docker exec ai-qa-ollama ollama pull nomic-embed-text

# Pull LLM model (choose one)
docker exec ai-qa-ollama ollama pull llama2        # 7B model (~4GB)
docker exec ai-qa-ollama ollama pull mistral       # 7B model (~4GB)
docker exec ai-qa-ollama ollama pull llama2:13b    # 13B model (~7GB)
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant UI: http://localhost:6333/dashboard

### First Steps

1. Open http://localhost:3000
2. Upload a document (PDF, DOCX, etc.)
3. Wait for processing to complete
4. Ask questions about your document!

## 📖 Usage Guide

### Uploading Documents

1. Click the upload area or drag & drop a file
2. Supported formats: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, JSON
3. Wait for processing (automatic chunking and embedding generation)
4. Document appears in "My Documents" list

### Asking Questions

1. Select a document or use "All Documents" to search across all files
2. Type your question in the chat input
3. Watch the AI generate a response in real-time
4. Click "sources" to see which document sections were used

### Example Questions

- "What is the main topic of this document?"
- "Summarize the key points in bullet form"
- "What does it say about [specific topic]?"
- "Compare the information between documents"
- "Extract all dates mentioned"

## ⚙️ Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# Ollama Models
EMBEDDING_MODEL=nomic-embed-text      # Embedding model
LLM_MODEL=llama2                      # Language model

# RAG Settings
CHUNK_SIZE=1000                       # Characters per chunk
CHUNK_OVERLAP=200                     # Overlap between chunks

# API Settings
CORS_ORIGINS=http://localhost:3000    # Allowed origins
```

### Changing Models

To use a different LLM:

1. Pull the model:
```bash
docker exec ai-qa-ollama ollama pull mistral
```

2. Update `.env`:
```bash
LLM_MODEL=mistral
```

3. Restart backend:
```bash
docker-compose restart backend
```

### Performance Tuning

**For better accuracy:**
- Increase `CHUNK_SIZE` (e.g., 1500)
- Increase `CHUNK_OVERLAP` (e.g., 300)
- Use larger models (llama2:13b)

**For faster responses:**
- Decrease `CHUNK_SIZE` (e.g., 500)
- Use smaller models (llama2:7b)
- Reduce `top_k` in queries

## 🔧 Development

### Project Structure

```
ai-document-qa/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   │   ├── upload.py      # File upload
│   │   ├── chat.py        # Chat/QA
│   │   └── documents.py   # Document management
│   ├── services/           # Business logic
│   │   ├── vector_store.py        # Qdrant integration
│   │   ├── embeddings.py          # Embedding generation
│   │   ├── llm.py                 # LLM integration
│   │   └── document_processor.py  # RAG pipeline
│   ├── utils/              # Utilities
│   │   ├── parsers.py     # Document parsers
│   │   └── chunking.py    # Text chunking
│   ├── main.py            # FastAPI app
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── App.tsx        # Main app
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Docker orchestration
└── README.md
```

### Running in Development Mode

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

### API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/upload          # Upload document
GET    /api/documents       # List documents
DELETE /api/documents/{id}  # Delete document
POST   /api/chat           # Ask question (streaming)
GET    /health             # Health check
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Ollama model not found

```bash
# List available models
docker exec ai-qa-ollama ollama list

# Pull required models
docker exec ai-qa-ollama ollama pull nomic-embed-text
docker exec ai-qa-ollama ollama pull llama2
```

### Out of memory errors

- Use smaller models
- Reduce chunk size
- Process fewer documents at once
- Increase Docker memory limit

### Slow responses

- Use smaller/faster models
- Enable GPU support
- Reduce document complexity
- Decrease chunk overlap

### Connection errors

```bash
# Check if all services are healthy
docker-compose ps

# Verify network
docker network ls
docker network inspect ai-qa-network
```

## 📊 Performance Tips

1. **GPU Acceleration** (if available):
   - Ensure NVIDIA Docker runtime is installed
   - GPU will be automatically used by Ollama

2. **Batch Processing**:
   - Upload multiple small documents together
   - System processes embeddings in batches

3. **Query Optimization**:
   - Be specific in questions
   - Use document filtering when possible
   - Adjust `top_k` based on document complexity

## 🔒 Security Notes

- This is a development setup - add authentication for production
- Uploaded documents are stored in Docker volumes
- API has CORS enabled for localhost - restrict for production
- No data is sent to external services (fully local)

## 📝 Advanced Features

### Custom Chunking Strategy

Edit `backend/services/document_processor.py`:
```python
processor = DocumentProcessor(
    chunk_size=1500,      # Larger chunks
    chunk_overlap=300     # More overlap
)
```

### Multiple Document Search

The system automatically searches across all uploaded documents when no specific document is selected.

### Citation Quality

Sources include:
- Document filename
- Chunk ID (position in document)
- Relevance score (0-1)
- Text excerpt

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional document format support
- Better chunking strategies
- UI/UX enhancements
- Performance optimizations
- Test coverage

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Ollama**: Local LLM inference
- **Qdrant**: Vector database
- **FastAPI**: Modern Python web framework
- **React**: UI framework
- **LangChain**: RAG utilities

## 📮 Support

For issues, questions, or suggestions:
1. Check existing documentation
2. Review troubleshooting section
3. Open an issue on GitHub

---

**Built with ❤️ for fast, accurate, and private document QA**
