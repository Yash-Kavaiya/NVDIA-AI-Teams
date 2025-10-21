"""Main processing pipeline."""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd
import aiohttp
from qdrant_client.models import PointStruct

from config.config import Config
from src.qdrant_manager import QdrantManager
from src.image_processor import ImageProcessor
from src.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)

class ImageEmbeddingPipeline:
    """Main pipeline for processing images and generating embeddings."""
    
    def __init__(self, config: Config):
        """Initialize pipeline."""
        self.config = config
        self.qdrant_manager = QdrantManager(config.qdrant)
        self.image_processor = ImageProcessor(config.processing)
        self.embedding_generator = EmbeddingGenerator(config.nvidia, config.processing)
        
        # Statistics
        self.success_count = 0
        self.failure_count = 0
        self.start_time = 0
    
    async def process_single_image(
        self,
        session: aiohttp.ClientSession,
        idx: int,
        filename: str,
        url: str,
        download_sem: asyncio.Semaphore,
        embedding_sem: asyncio.Semaphore
    ) -> Optional[PointStruct]:
        """Process single image: download, encode, generate embedding."""
        try:
            # Download image
            async with download_sem:
                image_data_uri = await self.image_processor.download_and_encode(session, url)
                if image_data_uri is None:
                    return None
            
            # Generate embedding
            async with embedding_sem:
                embedding = await self.embedding_generator.generate(session, image_data_uri)
                if embedding is None:
                    return None
            
            # Create point
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "filename": filename,
                    "image_url": url,
                    "processed": True,
                    "processed_at": datetime.now().isoformat()
                }
            )
            return point
            
        except Exception as e:
            logger.error(f"Error processing image {idx}: {e}")
            return None
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to human-readable time."""
        return str(timedelta(seconds=int(seconds)))
    
    def _print_progress(self, completed: int, total: int):
        """Print progress bar."""
        progress = completed / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        elapsed = time.time() - self.start_time
        if completed > 0:
            avg_time = elapsed / completed
            remaining = avg_time * (total - completed)
            eta = self._format_time(remaining)
        else:
            eta = "calculating..."
        
        print(f"\r[{bar}] {completed}/{total} ({progress*100:.1f}%) | "
              f"✓ {self.success_count} ✗ {self.failure_count} | ETA: {eta}", 
              end='', flush=True)
    
    async def process_csv(
        self, 
        csv_file: str, 
        start_from: int = 0, 
        max_images: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Process CSV file and store embeddings.
        
        Args:
            csv_file: Path to CSV file
            start_from: Row index to start from
            max_images: Maximum images to process
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        # Load CSV
        df = pd.read_csv(csv_file)
        logger.info(f"✓ Loaded {len(df)} rows from {csv_file}")
        
        # Rename columns
        if 'link' in df.columns:
            df = df.rename(columns={'link': 'url'})
        
        # Apply filters
        if start_from > 0:
            df = df.iloc[start_from:]
            logger.info(f"✓ Starting from row {start_from}")
        
        if max_images:
            df = df.head(max_images)
            logger.info(f"✓ Processing max {max_images} images")
        
        # Setup Qdrant
        self.qdrant_manager.create_collection_if_not_exists()
        
        total = len(df)
        self.success_count = 0
        self.failure_count = 0
        self.start_time = time.time()
        
        # Print header
        print(f"\n{'='*80}")
        print(f"Starting processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Concurrent downloads: {self.config.processing.concurrent_downloads}")
        print(f"Concurrent embeddings: {self.config.processing.concurrent_embeddings}")
        print(f"Batch size: {self.config.processing.batch_size}")
        print(f"{'='*80}\n")
        
        # Create semaphores
        download_sem = asyncio.Semaphore(self.config.processing.concurrent_downloads)
        embedding_sem = asyncio.Semaphore(self.config.processing.concurrent_embeddings)
        
        # Create session
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        async with aiohttp.ClientSession(connector=connector) as session:
            points_buffer = []
            tasks = []
            
            # Create tasks
            for idx, row in df.iterrows():
                filename = row.get('filename', '')
                url = row.get('url', '')
                
                if pd.isna(url) or not isinstance(url, str) or url.strip() == '':
                    self.failure_count += 1
                    continue
                
                task = self.process_single_image(
                    session, idx, filename, url, download_sem, embedding_sem
                )
                tasks.append(task)
            
            # Process tasks
            completed = 0
            for coro in asyncio.as_completed(tasks):
                result = await coro
                completed += 1
                
                if result is None:
                    self.failure_count += 1
                else:
                    points_buffer.append(result)
                    self.success_count += 1
                
                # Upload batch
                if len(points_buffer) >= self.config.processing.batch_size:
                    self.qdrant_manager.upsert_points(points_buffer)
                    points_buffer = []
                
                # Progress update
                if completed % 10 == 0 or completed == total:
                    self._print_progress(completed, total)
            
            # Upload remaining
            if points_buffer:
                self.qdrant_manager.upsert_points(points_buffer)
        
        # Print statistics
        self._print_statistics(total)
        
        return self.success_count, self.failure_count
    
    def _print_statistics(self, total: int):
        """Print final statistics."""
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{'='*80}")
        print(f"Processing Complete!")
        print(f"{'='*80}")
        print(f"✓ Successfully processed: {self.success_count:,} images")
        print(f"✗ Failed: {self.failure_count:,} images")
        
        if self.success_count + self.failure_count > 0:
            success_rate = (self.success_count / (self.success_count + self.failure_count)) * 100
            print(f"📊 Success rate: {success_rate:.1f}%")
        
        print(f"⏱️  Total time: {self._format_time(elapsed)}")
        
        if total > 0:
            print(f"⚡ Average time per image: {elapsed/total:.2f}s")
            print(f"🚀 Processing speed: {total/elapsed:.2f} images/second")
        
        print(f"💾 Collection: '{self.config.qdrant.collection_name}'")
        print(f"📐 Embedding dimension: {self.config.qdrant.embedding_dim}")
        print(f"{'='*80}\n")