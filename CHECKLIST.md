# ✅ Setup Checklist

Use this checklist to verify your AI Document QA System is properly set up.

## Pre-Installation

- [✅] Docker is installed (`docker --version`)
- [✅] Docker Compose is installed (`docker-compose --version`)
- [✅] At least 8GB RAM available
- [✅] At least 20GB disk space free
- [✅] Ports 3000, 6333, 8000, 11434 are available

## Installation

- [✅] Repository cloned/downloaded
- [✅] `.env` file created from `.env.example`
- [✅] Docker services started (`docker-compose up -d`)
- [✅] All containers running (`docker-compose ps`)

## Model Setup

- [✅] Ollama container is healthy
- [✅] Embedding model downloaded (`nomic-embed-text`)
- [✅] LLM model downloaded (`llama2` or alternative)
- [✅] Models verified (`docker exec ai-qa-ollama ollama list`)

## Service Health

- [✅] Backend is healthy (`curl http://localhost:8000/health`)
- [✅] Qdrant is accessible (`curl http://localhost:6333/health`)
- [✅] Ollama is responding (`curl http://localhost:11434/api/tags`)
- [✅] Frontend loads (`http://localhost:3000`)

## Functionality Tests

### Upload Test
- [✅] Navigate to http://localhost:3000
- [ ] Upload a test document (PDF/TXT)
- [ ] Document appears in "My Documents" list
- [ ] No error messages

### Chat Test
- [ ] Ask a question about the uploaded document
- [ ] Response is generated successfully
- [ ] Sources are displayed
- [ ] Answer is relevant to the question

### Document Management Test
- [ ] Click on a document to select it
- [ ] Delete a document
- [ ] Document is removed from list

## Performance Checks

- [ ] Upload completes in <30 seconds for typical documents
- [ ] Chat responses start streaming within 5 seconds
- [ ] No memory errors in logs
- [ ] No timeout errors

## Logs Verification

```bash
# Check backend logs
docker-compose logs backend | grep ERROR

# Should see no critical errors
```

- [ ] No critical errors in backend logs
- [ ] No errors in Qdrant logs
- [ ] No errors in Ollama logs
- [ ] No errors in frontend logs

## API Documentation

- [ ] Swagger UI accessible at `http://localhost:8000/docs`
- [ ] ReDoc accessible at `http://localhost:8000/redoc`
- [ ] API endpoints documented correctly

## Optional: Advanced Features

- [ ] GPU acceleration enabled (if available)
- [ ] Custom models configured
- [ ] Environment variables customized
- [ ] Production optimizations applied

## Troubleshooting

If any check fails, refer to:
- **SETUP.md** for detailed setup instructions
- **README.md** for troubleshooting section
- **Docker logs**: `docker-compose logs -f`

## Quick Commands Reference

```bash
# View all services status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Start fresh (removes data)
docker-compose down -v
docker-compose up -d

# Check models
docker exec ai-qa-ollama ollama list

# Pull new model
docker exec ai-qa-ollama ollama pull mistral

# Backend health
curl http://localhost:8000/health

# Qdrant health
curl http://localhost:6333/health
```

## Success Criteria

Your system is ready when:
✅ All services are running and healthy
✅ Models are downloaded
✅ You can upload a document
✅ You can ask questions and get answers
✅ No errors in logs

## Next Steps After Setup

1. ✅ Read the **README.md** for feature overview
2. ✅ Try the **API_GUIDE.md** for integration examples
3. ✅ Review **ARCHITECTURE.md** to understand the system
4. ✅ Customize settings in `.env` for your needs
5. ✅ Deploy to production (follow SETUP.md)

## Getting Help

If you encounter issues:
1. Check this checklist
2. Review **SETUP.md** troubleshooting section
3. Check Docker logs: `docker-compose logs`
4. Verify all prerequisites are met
5. Try restarting services: `docker-compose restart`

---

**Congratulations!** 🎉 If all checks pass, your AI Document QA System is ready to use!
