# ⚡ Quick Start Guide

Get up and running in 5 minutes!

## 1️⃣ Prerequisites

- Docker installed ✓
- Docker Compose installed ✓
- 8GB+ RAM ✓

## 2️⃣ Start Everything

```bash
# Option A: Use the automated script
./startup.sh

# Option B: Manual setup
cp .env.example .env
docker-compose up -d
docker exec ai-qa-ollama ollama pull nomic-embed-text
docker exec ai-qa-ollama ollama pull llama2
```

## 3️⃣ Open App

**Frontend**: http://localhost:3000

## 4️⃣ Test It

1. **Upload** a PDF/DOCX/TXT file
2. **Wait** for processing (~10-30 seconds)
3. **Ask** a question: "What is this document about?"
4. **Get** AI-powered answers with citations!

## 🎯 Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart everything
docker-compose restart

# Check health
curl http://localhost:8000/health
```

## 🔧 Troubleshooting

**Services won't start?**
```bash
docker-compose down
docker-compose up -d
```

**Models not found?**
```bash
docker exec ai-qa-ollama ollama pull nomic-embed-text
docker exec ai-qa-ollama ollama pull llama2
```

**Port conflicts?**
Edit `docker-compose.yml` and change port numbers.

## 📚 Next Steps

- Read full [README.md](README.md) for features
- See [SETUP.md](SETUP.md) for detailed setup
- Check [API Docs](http://localhost:8000/docs) for integration

## 🎉 That's It!

Your AI Document QA system is ready to use!
