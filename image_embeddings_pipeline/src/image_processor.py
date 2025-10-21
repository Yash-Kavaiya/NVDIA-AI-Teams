"""Image processing module."""
import base64
import io
import logging
from typing import Optional
import aiohttp
from PIL import Image
from config.config import ProcessingConfig

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image downloading and encoding."""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize image processor."""
        self.config = config
    
    async def download_and_encode(
        self, 
        session: aiohttp.ClientSession, 
        url: str
    ) -> Optional[str]:
        """
        Download image from URL and return base64 encoded data URI.
        
        Args:
            session: aiohttp session
            url: Image URL
            
        Returns:
            Base64 encoded data URI or None on failure
        """
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                content = await response.read()
                
                # Open and process image
                image = Image.open(io.BytesIO(content))
                
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize to reduce token usage
                max_size = (self.config.image_max_size, self.config.image_max_size)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Encode to base64
                buffer = io.BytesIO()
                image.save(
                    buffer, 
                    format="JPEG", 
                    quality=self.config.image_quality, 
                    optimize=True
                )
                img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return f"data:image/jpeg;base64,{img_b64}"
                
        except aiohttp.ClientError as e:
            logger.warning(f"HTTP error downloading {url}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error processing {url}: {e}")
            return None