"""
FastAPI application for IELTS Task 1 image metadata extraction.
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import io
from PIL import Image

from services.vision_service import get_vision_service


app = FastAPI(
    title="IELTS Metadata API",
    description="API for extracting structured metadata from IELTS Task 1 images",
    version="1.0.0"
)


class ImageURLRequest(BaseModel):
    """Request model for image URL."""
    image_url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/ielts-task1-image.jpg"
            }
        }


class BatchImageURLRequest(BaseModel):
    """Request model for batch processing of image URLs."""
    image_urls: List[HttpUrl]
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_urls": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ]
            }
        }


@app.on_event("startup")
async def startup_event():
    """Initialize the vision service on startup."""
    print("Starting IELTS Metadata API...")
    # Initialize the model (this will take some time on first run)
    get_vision_service()
    print("API ready to accept requests!")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "IELTS Task 1 Metadata Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "extract_from_url": "/api/extract/url",
            "extract_from_file": "/api/extract/file",
            "extract_batch": "/api/extract/batch",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": get_vision_service().model is not None
    }


@app.post("/api/extract/url")
async def extract_from_url(request: ImageURLRequest):
    """
    Extract metadata from an image URL.
    
    Args:
        request: ImageURLRequest containing the image URL
        
    Returns:
        JSON metadata extracted from the image
    """
    try:
        # Extract metadata (qwen_vl_utils handles URL download internally)
        vision_service = get_vision_service()
        metadata = vision_service.extract_metadata(str(request.image_url))
        
        return JSONResponse(content=metadata)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract metadata: {str(e)}"
        )


@app.post("/api/extract/file")
async def extract_from_file(file: UploadFile = File(...)):
    """
    Extract metadata from an uploaded image file.
    
    Args:
        file: Uploaded image file
        
    Returns:
        JSON metadata extracted from the image
    """
    try:
        # Read file contents
        image_bytes = await file.read()
        
        # Validate it's an image
        try:
            Image.open(io.BytesIO(image_bytes)).verify()
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image format: {str(e)}"
            )
        
        # Extract metadata
        vision_service = get_vision_service()
        metadata = vision_service.extract_metadata(image_bytes)
        
        return JSONResponse(content=metadata)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract metadata: {str(e)}"
        )


@app.post("/api/extract/batch")
async def extract_batch(request: BatchImageURLRequest):
    """
    Extract metadata from multiple image URLs in batch.
    
    Args:
        request: BatchImageURLRequest containing list of image URLs
        
    Returns:
        List of JSON metadata for each image
    """
    results = []
    vision_service = get_vision_service()
    
    for idx, image_url in enumerate(request.image_urls):
        try:
            # Extract metadata (qwen_vl_utils handles URL download internally)
            metadata = vision_service.extract_metadata(str(image_url))
            
            results.append({
                "image_url": str(image_url),
                "index": idx,
                "success": True,
                "metadata": metadata
            })
            
        except Exception as e:
            results.append({
                "image_url": str(image_url),
                "index": idx,
                "success": False,
                "error": str(e)
            })
    
    return JSONResponse(content={
        "total_images": len(request.image_urls),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
