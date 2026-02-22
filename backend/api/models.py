"""Models API endpoints"""
import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import httpx
import os

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/models")
async def list_models():
    """
    List all available Ollama models
    
    Returns list of models with name, size, and modified date
    """
    try:
        ollama_host = os.getenv("OLLAMA_HOST", "ollama")
        ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
        base_url = f"http://{ollama_host}:{ollama_port}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append({
                    "name": model.get("name", "").replace(":latest", ""),
                    "full_name": model.get("name", ""),
                    "size": model.get("size", 0),
                    "modified": model.get("modified_at", ""),
                    "description": get_model_description(model.get("name", ""))
                })
            
            return {
                "models": models,
                "default": os.getenv("LLM_MODEL", "llama2")
            }
            
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_model_description(model_name: str) -> str:
    """Get description for known models"""
    descriptions = {
        "llama2": "General purpose LLM - Good for English",
        "llama3.2": "Latest Llama model - Better multilingual support",
        "aya": "Multilingual model - Excellent for Arabic and 100+ languages",
        "nomic-embed-text": "Embedding model for document processing"
    }
    
    for key, desc in descriptions.items():
        if key in model_name:
            return desc
    
    return "Custom model"
