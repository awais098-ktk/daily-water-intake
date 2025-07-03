"""
LLaMA Processor for Water Intake Tracker
This module integrates a local LLaMA model for improved OCR text interpretation
"""

import os
import logging
import json
import re
from typing import Dict, Tuple, Optional, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLaMAProcessor:
    """
    LLaMA Processor for interpreting OCR text using a local LLaMA model
    """

    def __init__(self, model_path=None):
        """
        Initialize the LLaMA processor

        Args:
            model_path: Path to the local LLaMA model (optional)
        """
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.llm_pipe = None

        # Flag to indicate if LLaMA is available
        self.llama_available = False

        # Try to load the model if a path is provided
        if model_path:
            self.load_model(model_path)
        else:
            # Try to load a default model
            self.try_load_default_model()

    def try_load_default_model(self):
        """
        Try to load a default LLaMA model from common locations
        """
        try:
            # Try to import the transformers library
            try:
                import transformers
            except ImportError:
                # Silently handle missing transformers library
                self.llama_available = False
                return

            # List of common model names/paths to try
            model_names = [
                "meta-llama/Llama-2-7b-chat-hf",
                "TheBloke/Llama-2-7B-Chat-GGUF",
                "TheBloke/Llama-2-7b-Chat-GPTQ",
                "llama-2-7b-chat.Q4_K_M.gguf",  # Common filename for llama.cpp
                os.path.expanduser("~/llama-models/llama-2-7b-chat"),
                os.path.expanduser("~/models/llama-2-7b-chat"),
                "C:\\llama-models\\llama-2-7b-chat",
            ]

            for model_name in model_names:
                try:
                    # Silently try to load the model
                    self.load_model(model_name)
                    if self.llama_available:
                        break
                except Exception:
                    # Silently ignore errors
                    pass

            if not self.llama_available:
                # LLaMA is not available, but that's okay
                pass

        except Exception:
            # Silently handle any errors
            self.llama_available = False

    def load_model(self, model_path):
        """
        Load the LLaMA model from the specified path

        Args:
            model_path: Path to the LLaMA model
        """
        try:
            # Try to import the transformers library
            try:
                try:
                    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                except ImportError:
                    # Silently handle missing transformers library
                    self.llama_available = False
                    return

                # Load the tokenizer and model
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(model_path)

                # Create the pipeline
                self.llm_pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

                self.llama_available = True
            except Exception:
                # Silently handle any errors during model loading
                self.llama_available = False

        except Exception as e:
            # Silently handle errors
            self.llama_available = False

    def extract_brand_and_quantity(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract brand and quantity from OCR text using LLaMA

        Args:
            ocr_text: The OCR text to analyze

        Returns:
            Dictionary with brand and quantity information
        """
        if not ocr_text:
            logger.warning("No OCR text provided")
            return {"brand": None, "quantity_ml": None, "success": False}

        logger.info(f"Extracting brand and quantity from OCR text: {ocr_text}")

        # If LLaMA is available, use it for extraction
        if self.llama_available and self.llm_pipe:
            return self._extract_with_llama(ocr_text)
        else:
            # Fallback to regex-based extraction
            return self._extract_with_regex(ocr_text)

    def _extract_with_llama(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract brand and quantity using the LLaMA model

        Args:
            ocr_text: The OCR text to analyze

        Returns:
            Dictionary with brand and quantity information
        """
        try:
            # Create a prompt for the LLaMA model
            prompt = f"""Extract the brand and quantity (in ml) from this text:
{ocr_text}
Return in this format:
Brand: <brand>
Quantity: <value> ml"""

            # Generate a response from the model
            result = self.llm_pipe(prompt, max_new_tokens=100)[0]['generated_text']
            logger.info(f"LLaMA response: {result}")

            # Extract brand and quantity from the response
            brand_match = re.search(r'Brand:\s*(.+)', result)
            quantity_match = re.search(r'Quantity:\s*(\d+)', result)

            brand = brand_match.group(1).strip() if brand_match else None
            quantity_ml = int(quantity_match.group(1)) if quantity_match else None

            logger.info(f"Extracted brand: {brand}, quantity: {quantity_ml}ml")

            return {
                "brand": brand,
                "quantity_ml": quantity_ml,
                "success": brand is not None or quantity_ml is not None,
                "method": "llama"
            }

        except Exception as e:
            logger.error(f"Error extracting with LLaMA: {e}")
            # Fallback to regex-based extraction
            return self._extract_with_regex(ocr_text)

    def _extract_with_regex(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract brand and quantity using regex patterns (fallback method)

        Args:
            ocr_text: The OCR text to analyze

        Returns:
            Dictionary with brand and quantity information
        """
        logger.info("Using regex fallback for extraction")

        # Convert to lowercase for easier matching
        text_lower = ocr_text.lower()

        # Extract quantity using regex
        quantity_ml = None
        quantity_patterns = [
            r'(\d+)\s*ml',  # 500ml
            r'(\d+)\s*milliliter',  # 500 milliliters
            r'(\d+)\s*cl',  # 33cl
            r'(\d+)\s*l',  # 1l or 1 l
            r'(\d+\.\d+)\s*l',  # 1.5l
        ]

        for pattern in quantity_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = match.group(1)
                try:
                    if 'l' in pattern and '.' not in value:
                        # Convert liters to ml
                        quantity_ml = int(float(value) * 1000)
                    elif 'cl' in pattern:
                        # Convert centiliters to ml
                        quantity_ml = int(float(value) * 10)
                    else:
                        quantity_ml = int(value)
                    break
                except ValueError:
                    pass

        # Extract brand using common brand names
        brand = None
        brand_patterns = {
            'pepsi': 'Pepsi',
            'coca cola': 'Coca Cola',
            'coca-cola': 'Coca Cola',
            'coke': 'Coca Cola',
            'water': 'Water',
            'orange juice': 'Orange Juice',
            'apple juice': 'Apple Juice',
            'coffee': 'Coffee',
            'tea': 'Tea',
            'milk': 'Milk',
            'energy drink': 'Energy Drink',
            'red bull': 'Red Bull',
            'monster': 'Monster',
            'sparkling water': 'Sparkling Water',
            'lemonade': 'Lemonade',
            'iced tea': 'Iced Tea',
        }

        # Find the longest matching brand name
        max_length = 0
        for pattern, brand_name in brand_patterns.items():
            if pattern in text_lower and len(pattern) > max_length:
                brand = brand_name
                max_length = len(pattern)

        # If no brand found, use the first word as the brand
        if not brand and ocr_text:
            words = ocr_text.split()
            if words:
                brand = words[0].capitalize()

        logger.info(f"Extracted brand: {brand}, quantity: {quantity_ml}ml")

        return {
            "brand": brand,
            "quantity_ml": quantity_ml,
            "success": brand is not None or quantity_ml is not None,
            "method": "regex"
        }
