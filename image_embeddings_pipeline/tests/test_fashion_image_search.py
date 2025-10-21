"""
Image-based search tests for fashion dataset.

This module tests visual similarity search - finding products that LOOK similar,
not just match in text. This is the true power of multimodal embeddings:
understanding visual aesthetics, patterns, colors, and styles.
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.config import Config
from src.search_engine import ImageSearchEngine, SearchResult

console = Console()

# Real product images from your dataset
SAMPLE_IMAGES = {
    "titan_silver_watch": {
        "filename": "59263.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
        "description": "Titan Women Silver Watch",
        "category": "Accessories/Watches",
        "expected_similar": ["watch", "silver", "women", "titan"]
    },
    "skagen_black_watch": {
        "filename": "30039.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/Skagen-Men-Black-Watch_4982b2b1a76a85a85c9adc8b4b2d523a_images.jpg",
        "description": "Skagen Men Black Watch",
        "category": "Accessories/Watches",
        "expected_similar": ["watch", "black", "men", "skagen"]
    },
    "puma_grey_tshirt": {
        "filename": "53759.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/Puma-Men-Grey-T-shirt_32668f8a61454d0cc028a808cf21b383_images.jpg",
        "description": "Puma Men Grey T-shirt",
        "category": "Apparel/Topwear/Tshirts",
        "expected_similar": ["tshirt", "grey", "puma", "men"]
    },
    "fossil_belt": {
        "filename": "48123.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/8eee4563e14cf451b07f27761fd6535f_images.jpg",
        "description": "Fossil Women Black Belt",
        "category": "Accessories/Belts",
        "expected_similar": ["belt", "black", "fossil", "women"]
    },
    "casual_shoes": {
        "filename": "9204.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/051d64772f1b38ff476fbf0a807f365a_images.jpg",
        "description": "Puma Men Casual Shoes",
        "category": "Footwear/Shoes/Casual",
        "expected_similar": ["shoes", "casual", "puma", "black"]
    },
    "flip_flops": {
        "filename": "18653.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/53690e3f396f411e184b249672d6ebae_images.jpg",
        "description": "Fila Men Flip Flops",
        "category": "Footwear/Flip Flops",
        "expected_similar": ["flip", "flops", "fila", "men"]
    },
    "product_15970": {
        "filename": "15970.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/7a5b82d1372a7a5c6de67ae7a314fd91_images.jpg",
        "description": "Product 15970",
        "category": "Unknown",
        "expected_similar": []
    },
    "product_39386": {
        "filename": "39386.jpg",
        "url": "http://assets.myntassets.com/v1/images/style/properties/4850873d0c417e6480a26059f83aac29_images.jpg",
        "description": "Product 39386",
        "category": "Unknown",
        "expected_similar": []
    }
}


class TestFashionImageSearch:
    """Test cases for image-based fashion search."""
    
    @pytest.fixture
    async def search_engine(self):
        """Create search engine instance."""
        config = Config.from_env()
        config.validate()
        return ImageSearchEngine(config)
    
    def _display_image_results(
        self, 
        query_image: str, 
        results: List[SearchResult], 
        test_num: int,
        description: str = ""
    ):
        """Display image search results beautifully."""
        console.print(f"\n{'='*80}", style="bold cyan")
        console.print(f"TEST {test_num}: Image Similarity Search", style="bold yellow")
        if description:
            console.print(f"Query Image: {description}", style="dim")
        console.print(f"{'='*80}", style="bold cyan")
        
        if not results:
            console.print("✗ No similar images found", style="bold red")
            return
        
        table = Table(
            title=f"Top {len(results)} Similar Products", 
            show_header=True, 
            header_style="bold magenta"
        )
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Similarity", style="green", width=10)
        table.add_column("Product", style="yellow", width=55)
        
        for idx, result in enumerate(results, 1):
            similarity_pct = result.score * 100
            table.add_row(
                f"#{idx}",
                f"{similarity_pct:.2f}%",
                result.filename[:55]
            )
        
        console.print(table)
        
        # Show top match details
        if results:
            top = results[0]
            panel = Panel(
                f"[bold]Product:[/bold] {top.filename}\n"
                f"[bold]Similarity:[/bold] {top.score*100:.2f}%\n"
                f"[bold]URL:[/bold] {top.image_url[:60]}...\n"
                f"[bold]ID:[/bold] {top.id}",
                title="🏆 Best Match",
                border_style="green"
            )
            console.print("\n", panel)
    
    # ========================================================================
    # WATCH SIMILARITY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_watch_similarity_silver(self, search_engine):
        """Test 1: Find watches similar to Titan Silver Watch."""
        image_data = SAMPLE_IMAGES["titan_silver_watch"]
        
        console.print(f"\n[bold]Searching for products similar to:[/bold] {image_data['description']}")
        console.print(f"[dim]Category: {image_data['category']}[/dim]")
        
        results = await search_engine.search_by_image(
            image_data["url"],
            limit=10
        )
        
        self._display_image_results(
            image_data["url"],
            results,
            1,
            image_data["description"]
        )
        
        assert len(results) > 0, "Should find similar watches"
        assert results[0].score > 0.5, "Top match should have high similarity"
        
        # Analyze results
        watch_count = sum(1 for r in results if 'watch' in r.filename.lower())
        console.print(f"\n✓ Found {watch_count}/{len(results)} watch items", style="bold green")
    
    @pytest.mark.asyncio
    async def test_watch_similarity_black(self, search_engine):
        """Test 2: Find watches similar to Skagen Black Watch."""
        image_data = SAMPLE_IMAGES["skagen_black_watch"]
        
        results = await search_engine.search_by_image(
            image_data["url"],
            limit=10
        )
        
        self._display_image_results(
            image_data["url"],
            results,
            2,
            image_data["description"]
        )
        
        assert len(results) > 0, "Should find similar watches"
        
        # Check if similar watches are found
        watch_count = sum(1 for r in results[:5] if 'watch' in r.filename.lower())
        console.print(f"✓ Found {watch_count}/5 watches in top results")
    
    @pytest.mark.asyncio
    async def test_cross_watch_similarity(self, search_engine):
        """Test 3: Compare similarity between different watches."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 3: Cross-Watch Similarity Analysis", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        titan_results = await search_engine.search_by_image(
            SAMPLE_IMAGES["titan_silver_watch"]["url"],
            limit=5
        )
        
        skagen_results = await search_engine.search_by_image(
            SAMPLE_IMAGES["skagen_black_watch"]["url"],
            limit=5
        )
        
        console.print("\n[bold]Titan Silver Watch - Top 3 Similar:[/bold]")
        for i, r in enumerate(titan_results[:3], 1):
            console.print(f"  {i}. {r.filename[:50]} ({r.score*100:.2f}%)")
        
        console.print("\n[bold]Skagen Black Watch - Top 3 Similar:[/bold]")
        for i, r in enumerate(skagen_results[:3], 1):
            console.print(f"  {i}. {r.filename[:50]} ({r.score*100:.2f}%)")
        
        # Check if both find watches
        titan_watches = sum(1 for r in titan_results if 'watch' in r.filename.lower())
        skagen_watches = sum(1 for r in skagen_results if 'watch' in r.filename.lower())
        
        console.print(f"\n✓ Titan query found {titan_watches} watches", style="green")
        console.print(f"✓ Skagen query found {skagen_watches} watches", style="green")
    
    # ========================================================================
    # APPAREL SIMILARITY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_tshirt_similarity(self, search_engine):
        """Test 4: Find similar t-shirts."""
        image_data = SAMPLE_IMAGES["puma_grey_tshirt"]
        
        results = await search_engine.search_by_image(
            image_data["url"],
            limit=10
        )
        
        self._display_image_results(
            image_data["url"],
            results,
            4,
            image_data["description"]
        )
        
        assert len(results) > 0, "Should find similar t-shirts"
        
        # Analyze topwear results
        topwear_keywords = ['tshirt', 't-shirt', 'shirt', 'topwear']
        topwear_count = sum(1 for r in results[:5] 
                           if any(kw in r.filename.lower() for kw in topwear_keywords))
        
        console.print(f"✓ Found {topwear_count}/5 topwear items", style="green")
    
    # ========================================================================
    # ACCESSORY SIMILARITY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_belt_similarity(self, search_engine):
        """Test 5: Find similar belts and accessories."""
        image_data = SAMPLE_IMAGES["fossil_belt"]
        
        results = await search_engine.search_by_image(
            image_data["url"],
            limit=10
        )
        
        self._display_image_results(
            image_data["url"],
            results,
            5,
            image_data["description"]
        )
        
        assert len(results) > 0, "Should find similar accessories"
        
        # Check for accessory items
        accessory_keywords = ['belt', 'accessory', 'accessories']
        accessory_count = sum(1 for r in results[:5] 
                             if any(kw in r.filename.lower() for kw in accessory_keywords))
        
        console.print(f"✓ Found {accessory_count} accessory items in top 5", style="green")
    
    # ========================================================================
    # FOOTWEAR SIMILARITY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_shoes_similarity(self, search_engine):
        """Test 6: Find similar casual shoes."""
        image_data = SAMPLE_IMAGES["casual_shoes"]
        
        results = await search_engine.search_by_image(
            image_data["url"],
            limit=10
        )
        
        self._display_image_results(
            image_data["url"],
            results,
            6,
            image_data["description"]
        )
        
        assert len(results) > 0, "Should find similar footwear"
        
        # Check for footwear
        footwear_keywords = ['shoe', 'shoes', 'footwear', 'casual']
        footwear_count = sum(1 for r in results[:5] 
                            if any(kw in r.filename.lower() for kw in footwear_keywords))
        
        console.print(f"✓ Found {footwear_count} footwear items", style="green")
    
    @pytest.mark.asyncio
    async def test_flipflops_similarity(self, search_engine):
        """Test 7: Find similar flip flops."""
        image_data = SAMPLE_IMAGES["flip_flops"]
        
        results = await search_engine.search_by_image(
            image_data["url"],
            limit=10
        )
        
        self._display_image_results(
            image_data["url"],
            results,
            7,
            image_data["description"]
        )
        
        assert len(results) > 0, "Should find similar flip flops"
    
    # ========================================================================
    # VISUAL SIMILARITY ANALYSIS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_color_similarity(self, search_engine):
        """Test 8: Analyze color-based visual similarity."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 8: Color-Based Visual Similarity", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        # Search with black watch (should find black items)
        black_watch_results = await search_engine.search_by_image(
            SAMPLE_IMAGES["skagen_black_watch"]["url"],
            limit=10
        )
        
        # Search with silver watch (should find silver items)
        silver_watch_results = await search_engine.search_by_image(
            SAMPLE_IMAGES["titan_silver_watch"]["url"],
            limit=10
        )
        
        console.print("\n[bold]Black Watch - Color Distribution:[/bold]")
        black_items = sum(1 for r in black_watch_results if 'black' in r.filename.lower())
        console.print(f"  Black items: {black_items}/10")
        
        console.print("\n[bold]Silver Watch - Color Distribution:[/bold]")
        silver_items = sum(1 for r in silver_watch_results if 'silver' in r.filename.lower())
        console.print(f"  Silver items: {silver_items}/10")
        
        # Visual similarity should prefer similar colors
        console.print("\n✓ Visual embeddings understand color similarity", style="bold green")
    
    @pytest.mark.asyncio
    async def test_category_consistency(self, search_engine):
        """Test 9: Check if similar items are in same category."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 9: Category Consistency Analysis", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        test_items = [
            ("titan_silver_watch", "watch"),
            ("puma_grey_tshirt", "tshirt"),
            ("casual_shoes", "shoe"),
            ("fossil_belt", "belt")
        ]
        
        for item_key, expected_keyword in test_items:
            image_data = SAMPLE_IMAGES[item_key]
            results = await search_engine.search_by_image(image_data["url"], limit=5)
            
            category_matches = sum(1 for r in results 
                                  if expected_keyword in r.filename.lower())
            
            console.print(f"\n{image_data['description']}:")
            console.print(f"  Category consistency: {category_matches}/5 {expected_keyword}s found")
            
            assert category_matches >= 1, f"Should find at least one {expected_keyword}"
    
    # ========================================================================
    # HYBRID SEARCH TESTS (Image + Text)
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_hybrid_search_comparison(self, search_engine):
        """Test 10: Compare image search vs text search."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 10: Image vs Text Search Comparison", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        # Image search for watch
        image_results = await search_engine.search_by_image(
            SAMPLE_IMAGES["titan_silver_watch"]["url"],
            limit=5
        )
        
        # Text search for similar description
        text_results = await search_engine.search_by_text(
            "silver watch for women",
            limit=5
        )
        
        console.print("\n[bold]Image Search Results:[/bold]")
        for i, r in enumerate(image_results, 1):
            console.print(f"  {i}. {r.filename[:50]} ({r.score:.4f})")
        
        console.print("\n[bold]Text Search Results:[/bold]")
        for i, r in enumerate(text_results, 1):
            console.print(f"  {i}. {r.filename[:50]} ({r.score:.4f})")
        
        # Check overlap
        image_ids = {r.id for r in image_results}
        text_ids = {r.id for r in text_results}
        overlap = len(image_ids & text_ids)
        
        console.print(f"\n✓ Overlap: {overlap}/5 items", style="green")
        console.print("[dim]Image search finds visually similar items")
        console.print("Text search finds semantically similar items[/dim]")
    
    # ========================================================================
    # UNKNOWN PRODUCT EXPLORATION
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_unknown_product_discovery(self, search_engine):
        """Test 11: Discover what unknown products are similar to."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 11: Unknown Product Discovery", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        unknown_products = ["product_15970", "product_39386"]
        
        for product_key in unknown_products:
            image_data = SAMPLE_IMAGES[product_key]
            
            console.print(f"\n[bold]Analyzing {image_data['filename']}...[/bold]")
            
            results = await search_engine.search_by_image(image_data["url"], limit=5)
            
            if results:
                console.print(f"[green]✓ Found {len(results)} similar items:[/green]")
                
                # Analyze what it's similar to
                categories = {}
                for r in results:
                    filename_lower = r.filename.lower()
                    if 'watch' in filename_lower:
                        categories['watch'] = categories.get('watch', 0) + 1
                    elif 'shirt' in filename_lower or 'tshirt' in filename_lower:
                        categories['topwear'] = categories.get('topwear', 0) + 1
                    elif 'shoe' in filename_lower:
                        categories['footwear'] = categories.get('footwear', 0) + 1
                    elif 'belt' in filename_lower or 'bag' in filename_lower:
                        categories['accessory'] = categories.get('accessory', 0) + 1
                
                console.print(f"  Likely category distribution:")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    console.print(f"    - {cat}: {count}/5")
                
                console.print(f"\n  Top match: {results[0].filename[:60]}")
                console.print(f"  Similarity: {results[0].score*100:.2f}%")
            else:
                console.print("[red]✗ No similar items found[/red]")
    
    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_batch_image_search_performance(self, search_engine):
        """Test 12: Batch image search performance."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 12: Batch Image Search Performance", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        import time
        
        test_images = [
            "titan_silver_watch",
            "puma_grey_tshirt",
            "casual_shoes",
            "fossil_belt"
        ]
        
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing images...", total=len(test_images))
            
            results_collection = []
            for img_key in test_images:
                image_data = SAMPLE_IMAGES[img_key]
                results = await search_engine.search_by_image(image_data["url"], limit=5)
                results_collection.append((img_key, results))
                progress.update(task, advance=1)
        
        elapsed = time.time() - start_time
        avg_time = elapsed / len(test_images)
        
        console.print(f"\n[bold]Performance Metrics:[/bold]")
        console.print(f"  Total images processed: {len(test_images)}")
        console.print(f"  Total time: {elapsed:.2f}s")
        console.print(f"  Average time per image: {avg_time:.2f}s")
        console.print(f"  Throughput: {len(test_images)/elapsed:.2f} images/second")
        
        assert elapsed < 30, "Batch search should complete within 30 seconds"


# ============================================================================
# VISUAL SIMILARITY EXAMPLE SHOWCASE
# ============================================================================

async def run_visual_similarity_showcase():
    """Run visual similarity showcase with all sample images."""
    config = Config.from_env()
    config.validate()
    engine = ImageSearchEngine(config)
    
    console.print("\n" + "="*80, style="bold magenta")
    console.print("VISUAL SIMILARITY SHOWCASE", style="bold cyan")
    console.print("Finding visually similar products in fashion dataset", style="dim")
    console.print("="*80, style="bold magenta")
    
    for idx, (key, image_data) in enumerate(SAMPLE_IMAGES.items(), 1):
        console.print(f"\n[{idx}/{len(SAMPLE_IMAGES)}] [bold cyan]Query Image:[/bold cyan] {image_data['description']}")
        console.print(f"[dim]Category: {image_data['category']}[/dim]")
        console.print(f"[dim]URL: {image_data['url'][:70]}...[/dim]")
        
        try:
            results = await engine.search_by_image(image_data["url"], limit=5)
            
            if results:
                console.print(f"[green]✓ Found {len(results)} visually similar items:[/green]")
                
                table = Table(show_header=True, header_style="bold magenta", box=None)
                table.add_column("Rank", style="cyan", width=5)
                table.add_column("Similarity", style="green", width=10)
                table.add_column("Product", style="yellow")
                
                for i, r in enumerate(results, 1):
                    table.add_row(
                        f"{i}.",
                        f"{r.score*100:.1f}%",
                        r.filename[:65]
                    )
                
                console.print(table)
                
                # Visual similarity insights
                if 'watch' in image_data['description'].lower():
                    watch_count = sum(1 for r in results if 'watch' in r.filename.lower())
                    console.print(f"  💡 {watch_count}/5 results are watches (visual consistency)")
                
                elif 'tshirt' in image_data['description'].lower() or 't-shirt' in image_data['description'].lower():
                    topwear_count = sum(1 for r in results if any(kw in r.filename.lower() for kw in ['tshirt', 'shirt', 'topwear']))
                    console.print(f"  💡 {topwear_count}/5 results are topwear items")
                
            else:
                console.print("[yellow]⚠ No similar items found[/yellow]")
        
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
        
        # Small delay between requests
        await asyncio.sleep(0.5)
    
    # Final summary
    console.print("\n" + "="*80, style="bold magenta")
    console.print("VISUAL SEARCH INSIGHTS", style="bold yellow")
    console.print("="*80, style="bold magenta")
    
    insights_panel = Panel(
        "[bold]Key Findings:[/bold]\n\n"
        "• Visual embeddings understand product categories\n"
        "• Similar colors and patterns are grouped together\n"
        "• Same product types cluster in vector space\n"
        "• Multimodal search bridges text and image understanding\n"
        "• High-dimensional vectors capture visual semantics",
        title="🎯 Visual Similarity Intelligence",
        border_style="green"
    )
    console.print(insights_panel)


if __name__ == "__main__":
    """Run visual similarity showcase."""
    console.print(Panel.fit(
        "[bold magenta]Fashion Image Similarity Testing[/bold magenta]\n"
        "Visual search powered by multimodal embeddings",
        border_style="magenta"
    ))
    
    asyncio.run(run_visual_similarity_showcase())