"""FastAPI endpoints for Edge-AI malicious URL detection."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import Dict, List, Optional
import numpy as np
from pathlib import Path
import logging
import time
import psutil
import sys
sys.path.append('.')

from src.models import EdgeOptimizedModel
from src.features import URLLexicalFeatures, DomainMetadataFeatures
from src.utils import setup_logging, load_config

logger = setup_logging()

# FastAPI app
app = FastAPI(
    title="Edge-AI Malicious URL Detection API",
    description="Real-time malicious URL and domain detection using hybrid ML models",
    version="1.0.0"
)

# Global models
edge_model = None
url_feature_extractor = None
domain_feature_extractor = None

# Load models at startup
def startup_event():
    """Load models on startup.""" 
    global edge_model, url_feature_extractor, domain_feature_extractor
    
    try:
        logger.info("Loading edge-optimized models...")
        
        # Load models
        models_dir = Path("models")
        edge_model = EdgeOptimizedModel(models_dir)
        edge_model.load_models()
        
        # Load feature extractors
        url_feature_extractor = URLLexicalFeatures()
        domain_feature_extractor = DomainMetadataFeatures()
        
        logger.info("Models loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise

# Initialize models immediately
startup_event()

class URLRequest(BaseModel):
    """Single URL detection request."""
    url: str
    include_metadata: bool = False
    
    @validator('url')
    def validate_url(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("URL cannot be empty")
        return v.strip()

class BatchURLRequest(BaseModel):
    """Batch URL detection request."""
    urls: List[str]
    include_metadata: bool = False
    
    @validator('urls')
    def validate_urls(cls, v):
        if not v or len(v) == 0:
            raise ValueError("URLs list cannot be empty")
        if len(v) > 100:  # Limit batch size for edge deployment
            raise ValueError("Batch size cannot exceed 100 URLs")
        return [url.strip() for url in v if url.strip()]

class DetectionResponse(BaseModel):
    """Detection result for single URL."""
    url: str
    prediction: int  # 0 = benign, 1 = malicious
    probability: float
    label: str  # "benign" or "malicious"
    confidence: float
    processing_time_ms: float
    metadata: Optional[Dict] = None

class BatchDetectionResponse(BaseModel):
    """Batch detection results."""
    results: List[DetectionResponse]
    total_urls: int
    total_processing_time_ms: float
    system_stats: Optional[Dict] = None

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Edge-AI Malicious URL Detection",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "/detect": "Single URL detection",
            "/detect/batch": "Batch URL detection",
            "/health": "Health check",
            "/stats": "System statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    system_stats = get_system_stats()
    
    return {
        "status": "healthy" if edge_model is not None else "unhealthy",
        "models_loaded": edge_model is not None,
        "system": system_stats
    }

@app.get("/stats")
async def system_stats():
    """Get current system statistics."""
    return {
        "system": get_system_stats(),
        "models": {
            "loaded": edge_model is not None,
            "type": "Random Forest + Feature Engineering"
        }
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_url(request: URLRequest):
    """Detect if a single URL is malicious."""
    if edge_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    start_time = time.time()
    
    try:
        # Extract features
        features = url_feature_extractor.extract_features(request.url)
        
        # Make prediction
        result = edge_model.predict_single(features)
        
        processing_time = (time.time() - start_time) * 1000
        
        response = DetectionResponse(
            url=request.url,
            prediction=result['prediction'],
            probability=result['probability'],
            label=result['label'],
            confidence=result['confidence'],
            processing_time_ms=processing_time
        )
        
        if request.include_metadata:
            response.metadata = {
                "features_extracted": len(features),
                "model_type": "Random Forest"
            }
            
        return response
        
    except Exception as e:
        logger.error(f"Detection error for URL {request.url}: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.post("/detect/batch", response_model=BatchDetectionResponse)
async def detect_urls_batch(request: BatchURLRequest):
    """Detect if multiple URLs are malicious."""
    if edge_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    start_time = time.time()
    results = []
    
    try:
        # Process each URL
        for url in request.urls:
            url_start_time = time.time()
            
            # Extract features
            features = url_feature_extractor.extract_features(url)
            
            # Make prediction
            result = edge_model.predict_single(features)
            
            url_processing_time = (time.time() - url_start_time) * 1000
            
            detection_result = DetectionResponse(
                url=url,
                prediction=result['prediction'],
                probability=result['probability'],
                label=result['label'],
                confidence=result['confidence'],
                processing_time_ms=url_processing_time
            )
            
            if request.include_metadata:
                detection_result.metadata = {
                    "features_extracted": len(features),
                    "model_type": "Random Forest"
                }
                
            results.append(detection_result)
        
        total_processing_time = (time.time() - start_time) * 1000
        
        response = BatchDetectionResponse(
            results=results,
            total_urls=len(request.urls),
            total_processing_time_ms=total_processing_time,
            system_stats=get_system_stats() if request.include_metadata else None
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Batch detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")

def get_system_stats() -> Dict:
    """Get current system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / 1024 / 1024,
            "memory_used_mb": memory.used / 1024 / 1024
        }
    except Exception:
        return {"error": "Unable to get system stats"}

if __name__ == "__main__":
    import uvicorn
    
    config = load_config()
    api_config = config['api']
    
    uvicorn.run(
        "src.api.main:app",
        host=api_config['host'],
        port=api_config['port'],
        reload=api_config['reload'],
        log_level=api_config['log_level']
    )