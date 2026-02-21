# 🚀 Detailed Setup Guide

Complete setup instructions for the AI Document QA System.

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: 8GB (16GB recommended)
- **Storage**: 20GB free space
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Recommended Requirements
- **RAM**: 16GB+
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for faster inference)
- **Storage**: 50GB+ SSD

## Installation Steps

### 1. Install Docker

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

#### macOS
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop from Applications
```

#### Windows
1. Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
2. Install Docker Desktop: https://www.docker.com/products/docker-desktop
3. Enable WSL2 integration in Docker Desktop settings

### 2. (Optional) Install NVIDIA Docker for GPU Support

Only if you have an NVIDIA GPU:

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-docker2
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker
sudo systemctl restart docker
```

### 3. Clone and Setup Project

```bash
# Clone repository
git clone <repository-url>
cd ai-document-qa

# Create environment file
cp .env.example .env

# (Optional) Edit .env to customize settings
nano .env
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Expected output:
```
NAME                STATUS              PORTS
ai-qa-ollama       Up (healthy)        0.0.0.0:11434->11434/tcp
ai-qa-qdrant       Up (healthy)        0.0.0.0:6333->6333/tcp
ai-qa-backend      Up                  0.0.0.0:8000->8000/tcp
ai-qa-frontend     Up                  0.0.0.0:3000->3000/tcp
```

### 5. Download AI Models

This is the **most important step**! The system won't work without these models.

```bash
# Pull embedding model (required, ~275MB)
docker exec ai-qa-ollama ollama pull nomic-embed-text

# Pull LLM model - choose ONE:

# Option 1: Llama2 7B (recommended, ~4GB)
docker exec ai-qa-ollama ollama pull llama2

# Option 2: Mistral 7B (alternative, ~4GB)
docker exec ai-qa-ollama ollama pull mistral

# Option 3: Llama2 13B (better quality, ~7GB)
docker exec ai-qa-ollama ollama pull llama2:13b

# Verify models are installed
docker exec ai-qa-ollama ollama list
```

### 6. Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"api":"healthy","qdrant":"healthy","ollama":"healthy"}

# Open frontend
open http://localhost:3000  # macOS
# or
xdg-open http://localhost:3000  # Linux
# or visit http://localhost:3000 in browser
```

## Configuration

### Using Different Models

To use a different LLM model:

1. **Pull the model:**
```bash
docker exec ai-qa-ollama ollama pull mistral
```

2. **Update `.env`:**
```bash
LLM_MODEL=mistral
```

3. **Restart backend:**
```bash
docker-compose restart backend
```

### Available Models

Popular Ollama models:
- `llama2` - 7B general purpose (4GB)
- `llama2:13b` - 13B better quality (7GB)
- `mistral` - 7B fast and efficient (4GB)
- `mixtral` - 47B expert model (26GB)
- `codellama` - 7B code-focused (4GB)
- `neural-chat` - 7B conversational (4GB)

Browse more: https://ollama.ai/library

### Customizing RAG Settings

Edit `.env` file:

```bash
# Text chunking
CHUNK_SIZE=1000          # Characters per chunk (500-2000)
CHUNK_OVERLAP=200        # Overlap between chunks (100-400)

# Search
TOP_K=5                  # Number of relevant chunks (3-10)

# Models
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama2
```

**Guidelines:**
- **Larger chunks** = Better context, slower processing
- **More overlap** = Better accuracy, more storage
- **Higher top_k** = More context, slower responses

## Production Deployment

### Security Hardening

1. **Enable authentication** (add to backend):
```python
from fastapi.security import HTTPBearer
```

2. **Restrict CORS:**
```bash
CORS_ORIGINS=https://yourdomain.com
```

3. **Use HTTPS:**
```yaml
# Add nginx reverse proxy
nginx:
  image: nginx:alpine
  ports:
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
```

4. **Set resource limits:**
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
services:
  frontend:
    build:
      target: production  # Use nginx production build
    ports:
      - "80:80"
```

Deploy:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Scaling

For high-traffic deployments:

1. **Use external Qdrant:**
```yaml
# Remove qdrant service, point to cloud Qdrant
environment:
  QDRANT_HOST=your-qdrant-cloud.com
  QDRANT_PORT=6333
```

2. **Scale backend:**
```bash
docker-compose up -d --scale backend=3
```

3. **Add load balancer:**
```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Resource Usage

```bash
# Check container stats
docker stats

# Check disk usage
docker system df
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Qdrant
curl http://localhost:6333/health

# Ollama
curl http://localhost:11434/api/tags
```

## Backup & Restore

### Backup

```bash
# Backup Qdrant data
docker run --rm -v ai-document-qa_qdrant_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant-backup.tar.gz /data

# Backup Ollama models
docker run --rm -v ai-document-qa_ollama_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama-backup.tar.gz /data
```

### Restore

```bash
# Restore Qdrant data
docker run --rm -v ai-document-qa_qdrant_data:/data -v $(pwd):/backup \
  alpine sh -c "cd / && tar xzf /backup/qdrant-backup.tar.gz"

# Restore Ollama models
docker run --rm -v ai-document-qa_ollama_data:/data -v $(pwd):/backup \
  alpine sh -c "cd / && tar xzf /backup/ollama-backup.tar.gz"
```

## Uninstallation

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove images
docker rmi $(docker images -q 'ai-qa-*')
```

## Common Issues

### Port Already in Use

```bash
# Change ports in docker-compose.yml
ports:
  - "3001:3000"  # Use different host port
```

### Out of Disk Space

```bash
# Clean up Docker
docker system prune -a

# Remove old images
docker image prune -a
```

### Cannot Connect to Services

```bash
# Check firewall
sudo ufw allow 8000
sudo ufw allow 3000

# Check Docker network
docker network inspect ai-qa-network
```

## Next Steps

1. ✅ Verify all services are running
2. ✅ Models are downloaded
3. ✅ Upload a test document
4. ✅ Ask a test question
5. 📖 Read the main README for usage guide
6. 🎨 Customize the UI (frontend/src/App.tsx)
7. ⚙️ Tune RAG parameters for your use case

## Getting Help

- 📖 Documentation: README.md
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📊 API Docs: http://localhost:8000/docs

Happy document questioning! 🚀
