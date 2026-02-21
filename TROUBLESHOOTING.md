# Troubleshooting Guide

## "Failed to load documents" Error

This error typically occurs when the frontend cannot connect to the backend API.

### Solution 1: Check if you're using Lightning Studio

If you're running this in **Lightning Studio**, you need to access the services through the studio's proxy URLs, not `localhost`.

**Steps:**

1. **Find your studio URLs:**
   - Frontend: Click on the "3000" port in Lightning Studio's port panel
   - Backend: Click on the "8000" port in Lightning Studio's port panel

2. **Update the frontend environment variable:**
   ```bash
   # Edit .env file and change REACT_APP_API_URL
   # From:
   REACT_APP_API_URL=http://localhost:8000
   
   # To (use your actual studio backend URL):
   REACT_APP_API_URL=https://your-studio-id-8000.lightning.ai
   ```

3. **Rebuild the frontend:**
   ```bash
   docker compose restart frontend
   ```

### Solution 2: Running on Local Machine

If you're running on your local machine:

1. **Verify services are running:**
   ```bash
   docker compose ps
   ```
   All services should show "Up" and "healthy" status.

2. **Test API directly:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"api":"healthy","qdrant":"healthy","ollama":"healthy"}`

3. **Test documents endpoint:**
   ```bash
   curl http://localhost:8000/api/documents
   ```
   Should return: `[]` (empty array if no documents uploaded)

4. **Check browser console:**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for any CORS or network errors
   - If you see CORS errors, the API URL might be wrong

### Solution 3: Fix CORS Issues

If you see CORS errors in the browser console:

1. **Update CORS origins in .env:**
   ```bash
   CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.lightning.ai
   ```

2. **Restart backend:**
   ```bash
   docker compose restart backend
   ```

### Solution 4: Network Issues

If services can't reach each other:

1. **Check Docker network:**
   ```bash
   docker network ls
   docker network inspect this_studio_ai-qa-network
   ```

2. **Restart all services:**
   ```bash
   docker compose down
   docker compose up -d
   ```

3. **Check logs:**
   ```bash
   docker compose logs frontend
   docker compose logs backend
   ```

## Quick Diagnostics

Run this command to check system health:

```bash
# Check all services
docker compose ps

# Test backend from host
curl http://localhost:8000/health

# Test API endpoint
curl http://localhost:8000/api/documents

# Check frontend logs
docker compose logs frontend --tail 20

# Check backend logs
docker compose logs backend --tail 20
```

## Common Issues

### Issue: "Cannot connect to backend"
**Solution:** Make sure REACT_APP_API_URL points to the correct backend URL for your environment.

### Issue: "CORS policy blocked"
**Solution:** Add your frontend URL to CORS_ORIGINS in .env and restart backend.

### Issue: "Services not healthy"
**Solution:** Wait 30-60 seconds for health checks to pass, or check logs for errors.

### Issue: "Port already in use"
**Solution:** 
```bash
# Find what's using the port
lsof -i :3000
lsof -i :8000

# Or change ports in docker-compose.yml
```

## For Lightning Studio Users

### Getting Your Studio URLs

1. Look at the Lightning Studio UI - there's a "Ports" panel
2. Click on each port (3000, 8000) to get the public URL
3. The URLs will look like: `https://01234567-8000.lightning.ai`

### Update Environment for Studio

```bash
# In .env file, use your actual studio URLs
REACT_APP_API_URL=https://your-studio-id-8000.lightning.ai
CORS_ORIGINS=https://your-studio-id-3000.lightning.ai
```

Then restart:
```bash
docker compose restart
```

## Still Having Issues?

1. **Check all logs:**
   ```bash
   docker compose logs
   ```

2. **Verify environment:**
   ```bash
   cat .env
   docker compose exec frontend printenv | grep REACT_APP
   ```

3. **Test from browser console:**
   ```javascript
   fetch('http://localhost:8000/health')
     .then(r => r.json())
     .then(console.log)
   ```

4. **Clear browser cache and reload**

5. **Restart everything:**
   ```bash
   docker compose down
   docker compose up -d
   ```
