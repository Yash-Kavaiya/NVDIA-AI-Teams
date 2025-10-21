"""Embedding generation module."""
import logging
from typing import Optional, List
import aiohttp
from config.config import NvidiaConfig, ProcessingConfig

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generates embeddings using NVIDIA API."""
    
    def __init__(self, nvidia_config: NvidiaConfig, processing_config: ProcessingConfig):
        """Initialize embedding generator."""
        self.nvidia_config = nvidia_config
        self.processing_config = processing_config
    
    async def generate(
        self, 
        session: aiohttp.ClientSession, 
        image_data_uri: str
    ) -> Optional[List[float]]:
        """
        Generate embedding for image.
        
        Args:
            session: aiohttp session
            image_data_uri: Base64 encoded image data URI
            
        Returns:
            Embedding vector or None on failure
        """
        payload = {
            "input": [image_data_uri],
            "model": self.nvidia_config.model,
            "encoding_format": self.nvidia_config.encoding_format
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.processing_config.request_timeout)
            async with session.post(
                self.nvidia_config.embedding_url,
                json=payload,
                headers=self.nvidia_config.headers,
                timeout=timeout
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
                
                logger.warning("No embedding in API response")
                return None
                
        except aiohttp.ClientError as e:
            logger.warning(f"HTTP error generating embedding: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error generating embedding: {e}")
            return None