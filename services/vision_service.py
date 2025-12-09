"""
Vision service for extracting IELTS Task 1 image metadata using Qwen2.5-VL model.
"""
import torch
import json
from typing import Optional, Union
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
from utils.prompts import IELTS_TASK1_VISION_SYSTEM_PROMPT


class VisionService:
    """Service for processing IELTS Task 1 images and extracting metadata."""
    
    def __init__(self, model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct"):
        """
        Initialize the vision service with the Qwen2.5-VL model.
        
        Args:
            model_name: The name of the model to use
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model with 4-bit quantization for efficient inference."""
        print(f"Initializing {self.model_name}...")
        
        # Check GPU availability
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            print("Warning: No GPU detected. Model will run on CPU (very slow).")
        
        # Configure 4-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load model
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self.model_name,
            quantization_config=quantization_config,
            device_map="auto",
        )
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        
        print("Model loaded successfully with 4-bit quantization!")
    
    def extract_metadata(self, image_data: Union[str, bytes]) -> dict:
        """
        Extract structured metadata from IELTS Task 1 image.
        
        Args:
            image_data: Image URL or image bytes
            
        Returns:
            dict: Structured metadata as JSON
        """
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not initialized")
        
        # Prepare messages for the model
        messages = [
            {
                "role": "system",
                "content": IELTS_TASK1_VISION_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_data,
                    },
                    {
                        "type": "text",
                        "text": "Analyze this IELTS Task 1 image and provide the complete JSON metadata as specified."
                    },
                ],
            }
        ]
        
        # Prepare for inference
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.model.device)
        
        # Generate output
        with torch.no_grad():
            generated_ids = self.model.generate(**inputs, max_new_tokens=2048)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )
        
        # Parse JSON output
        try:
            metadata = json.loads(output_text[0])
            return metadata
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return the raw output with error info
            return {
                "error": "Failed to parse JSON output",
                "error_details": str(e),
                "raw_output": output_text[0]
            }


# Global instance
_vision_service: Optional[VisionService] = None


def get_vision_service() -> VisionService:
    """
    Get or create the global vision service instance.
    
    Returns:
        VisionService: The global vision service instance
    """
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
