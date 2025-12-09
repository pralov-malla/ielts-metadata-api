# IELTS Metadata API

FastAPI application for extracting structured metadata from IELTS Task 1 images using Qwen2.5-VL-7B-Instruct model.

## Features

- **Single Image Extraction**: Extract metadata from a single image via URL or file upload
- **Batch Processing**: Process multiple images in a single request
- **Structured JSON Output**: Returns comprehensive metadata following IELTS Task 1 schema
- **GPU Acceleration**: Optimized with 4-bit quantization for efficient inference
- **RESTful API**: Clean and well-documented API endpoints

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended, 8GB+ VRAM)
- 10GB+ disk space for model downloads

## Installation

1. **Clone or navigate to the repository**:

```powershell
cd e:\ielts-metadata-api
```

2. **Create and activate virtual environment**:

```powershell
python -m venv metadata
.\metadata\Scripts\Activate.ps1
```

3. **Install dependencies**:

```powershell
pip install -r requirements.txt
```

## Running the API

### Start the server:

```powershell
python run.py
```

Or using uvicorn directly:

```powershell
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### First Run

The first request will take several minutes as the model downloads and initializes. Subsequent requests will be faster.

## API Endpoints

### 1. Extract from URL

**POST** `/api/extract/url`

Extract metadata from an image URL.

**Request body**:

```json
{
  "image_url": "https://example.com/ielts-task1-image.jpg"
}
```

**Example with curl**:

```powershell
curl -X POST "http://localhost:8000/api/extract/url" `
  -H "Content-Type: application/json" `
  -d '{\"image_url\": \"https://example.com/image.jpg\"}'
```

### 2. Extract from File

**POST** `/api/extract/file`

Extract metadata from an uploaded image file.

**Example with curl**:

```powershell
curl -X POST "http://localhost:8000/api/extract/file" `
  -F "file=@path/to/image.jpg"
```

### 3. Batch Extraction

**POST** `/api/extract/batch`

Extract metadata from multiple images.

**Request body**:

```json
{
  "image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

### 4. Health Check

**GET** `/health`

Check API health and model status.

## Response Format

The API returns structured JSON metadata following the IELTS Task 1 schema:

```json
{
  "schema_version": "task1_v1",
  "task_visual_category": "bar_chart",
  "topic_context": {
    "title": "Population by Age Group",
    "time_dimension": {
      "has_time_dimension": true,
      "time_unit": "year",
      "start": "1990",
      "end": "2020"
    }
  },
  "global_semantics": {
    "primary_overview": "The chart shows population changes...",
    "primary_features": [...]
  },
  "visuals": [...],
  "raw_text_elements": [...],
  "extraction_notes": {...}
}
```

## Testing

Run the test script:

```powershell
python test_api.py
```

Make sure to update the test URLs and file paths in `test_api.py` before running.

## Project Structure

```
ielts-metadata-api/
├── services/
│   ├── __init__.py
│   └── vision_service.py    # Vision model service
├── utils/
│   ├── __init__.py
│   └── prompts.py           # System prompts for the model
├── metadata/                 # Virtual environment (gitignored)
├── .env.example             # Environment variables template
├── .gitignore
├── app.py                   # FastAPI application
├── README.md
├── requirements.txt
├── run.py                   # Server runner script
└── test_api.py             # API test script
```

## Configuration

Environment variables (optional, create `.env` file):

```
HOST=0.0.0.0
PORT=8000
MODEL_NAME=Qwen/Qwen2.5-VL-7B-Instruct
CUDA_VISIBLE_DEVICES=0
```

## Performance Tips

1. **GPU Memory**: The model uses ~7GB VRAM with 4-bit quantization
2. **Batch Processing**: Use the batch endpoint for multiple images to optimize throughput
3. **Timeout**: First request may take 30-60 seconds for model loading
4. **Caching**: Model weights are cached after first download

## Troubleshooting

### GPU Not Detected

```
Warning: No GPU detected. Model will run on CPU (very slow).
```

**Solution**: Install CUDA-compatible PyTorch:

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory

**Solution**: Close other GPU applications or reduce batch size

### Model Download Issues

**Solution**: Check internet connection and disk space (need 10GB+)

## License

This project uses the Qwen2.5-VL-7B-Instruct model. Please refer to the model's license for usage terms.

## Support

For issues and questions, please check:

- API documentation: http://localhost:8000/docs
- Model documentation: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
