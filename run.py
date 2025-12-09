"""
Script to run the IELTS Metadata API server.
"""
import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting IELTS Metadata API on {host}:{port}")
    print("Note: First request will be slow as the model loads.")
    print("API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
