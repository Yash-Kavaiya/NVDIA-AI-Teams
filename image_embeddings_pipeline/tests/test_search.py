"""
Test suite for fashion and clothing image search.

This suite validates semantic understanding of:
- Apparel categories (shirts, pants, dresses, etc.)
- Accessories (watches, bags, belts, etc.)
- Colors and patterns
- Seasons and occasions
- Gender-specific items
- Brand recognition
- Style combinations
"""
import asyncio
import sys
from pathlib import Path
from typing import List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config.config import Config
from src.search_engine import ImageSearchEngine, SearchResult

console = Console()


class TestFashionSearch:
    """Comprehensive test cases for fashion image search."""
    
    @pytest.fixture
    async def search_engine(self):
        """Create search engine instance for fashion dataset."""
        config = Config.from_env()
        config.validate()
        return ImageSearchEngine(config)
    
    def _display_results(self, query: str, results: List[SearchResult], test_num: int):
        """Display search results in a beautiful table."""
        console.print(f"\n{'='*80}", style="bold cyan")
        console.print(f"TEST {test_num}: {query}", style="bold yellow")
        console.print(f"{'='*80}", style="bold cyan")
        
        if not results:
            console.print("✗ No results found", style="bold red")
            return
        
        table = Table(title=f"Found {len(results)} Results", show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Score", style="green", width=8)
        table.add_column("Product", style="yellow", width=60)
        
        for idx, result in enumerate(results, 1):
            table.add_row(
                f"#{idx}",
                f"{result.score:.4f}",
                result.filename[:60]
            )
        
        console.print(table)
    
    # ========================================================================
    # CATEGORY-BASED TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_mens_shirts(self, search_engine):
        """Test 1: Search for men's shirts."""
        query = "men's casual shirt"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 1)
        
        assert len(results) > 0, "Should find men's shirts"
        assert results[0].score > 0.4, "Top result should have reasonable confidence"
        
        # Check if results contain shirt-related keywords
        shirt_count = sum(1 for r in results[:5] if 'shirt' in r.filename.lower())
        assert shirt_count >= 1, "Top results should contain shirts"
    
    @pytest.mark.asyncio
    async def test_womens_dresses(self, search_engine):
        """Test 2: Search for women's dresses."""
        query = "elegant women's dress"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 2)
        
        assert len(results) > 0, "Should find women's dresses"
    
    @pytest.mark.asyncio
    async def test_mens_bottomwear(self, search_engine):
        """Test 3: Search for men's pants/trousers."""
        query = "men's black track pants"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 3)
        
        assert len(results) > 0, "Should find men's bottomwear"
        
        # Check for pants-related items
        pants_keywords = ['pant', 'trouser', 'track', 'jean']
        pants_found = sum(1 for r in results[:5] 
                         if any(kw in r.filename.lower() for kw in pants_keywords))
        console.print(f"✓ Found {pants_found}/5 pants-related items in top results")
    
    @pytest.mark.asyncio
    async def test_tshirts(self, search_engine):
        """Test 4: Search for t-shirts."""
        query = "grey t-shirt for summer"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 4)
        
        assert len(results) > 0, "Should find t-shirts"
        
        # Verify t-shirt results
        tshirt_count = sum(1 for r in results[:5] if 'tshirt' in r.filename.lower() or 't-shirt' in r.filename.lower())
        console.print(f"✓ Found {tshirt_count}/5 t-shirt items")
    
    # ========================================================================
    # ACCESSORY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_watches(self, search_engine):
        """Test 5: Search for watches."""
        query = "silver watch for women"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 5)
        
        assert len(results) > 0, "Should find watches"
        
        watch_count = sum(1 for r in results[:5] if 'watch' in r.filename.lower())
        assert watch_count >= 1, "Should find watch items"
        console.print(f"✓ Found {watch_count} watches in top 5 results")
    
    @pytest.mark.asyncio
    async def test_handbags(self, search_engine):
        """Test 6: Search for handbags."""
        query = "women's blue handbag"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 6)
        
        assert len(results) > 0, "Should find handbags"
        
        bag_keywords = ['bag', 'handbag', 'purse']
        bag_count = sum(1 for r in results[:5] 
                       if any(kw in r.filename.lower() for kw in bag_keywords))
        console.print(f"✓ Found {bag_count} bag items")
    
    @pytest.mark.asyncio
    async def test_belts(self, search_engine):
        """Test 7: Search for belts."""
        query = "black leather belt"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 7)
        
        assert len(results) > 0, "Should find belts"
    
    # ========================================================================
    # FOOTWEAR TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_casual_shoes(self, search_engine):
        """Test 8: Search for casual shoes."""
        query = "men's black casual shoes"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 8)
        
        assert len(results) > 0, "Should find casual shoes"
        
        shoe_keywords = ['shoe', 'shoes', 'casual']
        shoe_count = sum(1 for r in results[:5] 
                        if any(kw in r.filename.lower() for kw in shoe_keywords))
        console.print(f"✓ Found {shoe_count} shoe items")
    
    @pytest.mark.asyncio
    async def test_flip_flops(self, search_engine):
        """Test 9: Search for flip flops/slippers."""
        query = "comfortable flip flops for summer"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 9)
        
        assert len(results) > 0, "Should find flip flops"
    
    # ========================================================================
    # COLOR-BASED TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_black_clothing(self, search_engine):
        """Test 10: Search for black colored items."""
        query = "black clothing items"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 10)
        
        assert len(results) > 0, "Should find black items"
        
        black_count = sum(1 for r in results[:10] if 'black' in r.filename.lower())
        console.print(f"✓ Found {black_count}/10 black items")
        assert black_count >= 3, "Should find multiple black items"
    
    @pytest.mark.asyncio
    async def test_grey_clothing(self, search_engine):
        """Test 11: Search for grey colored items."""
        query = "grey or gray apparel"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 11)
        
        assert len(results) > 0, "Should find grey items"
    
    @pytest.mark.asyncio
    async def test_blue_items(self, search_engine):
        """Test 12: Search for blue items."""
        query = "navy blue accessories"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 12)
        
        assert len(results) > 0, "Should find blue items"
    
    # ========================================================================
    # SEASON-BASED TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_summer_wear(self, search_engine):
        """Test 13: Search for summer clothing."""
        query = "light summer clothing"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 13)
        
        assert len(results) > 0, "Should find summer items"
        
        summer_count = sum(1 for r in results[:10] if 'summer' in r.filename.lower())
        console.print(f"✓ Found {summer_count} summer items")
    
    @pytest.mark.asyncio
    async def test_winter_wear(self, search_engine):
        """Test 14: Search for winter accessories."""
        query = "winter accessories and clothing"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 14)
        
        assert len(results) > 0, "Should find winter items"
    
    # ========================================================================
    # STYLE/OCCASION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_casual_wear(self, search_engine):
        """Test 15: Search for casual clothing."""
        query = "casual everyday wear"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 15)
        
        assert len(results) > 0, "Should find casual items"
        
        casual_count = sum(1 for r in results[:10] if 'casual' in r.filename.lower())
        console.print(f"✓ Found {casual_count} casual items")
    
    @pytest.mark.asyncio
    async def test_ethnic_wear(self, search_engine):
        """Test 16: Search for ethnic/traditional clothing."""
        query = "ethnic traditional clothing"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 16)
        
        assert len(results) > 0, "Should find ethnic wear"
    
    # ========================================================================
    # BRAND-SPECIFIC TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_puma_products(self, search_engine):
        """Test 17: Search for Puma brand items."""
        query = "Puma sportswear"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 17)
        
        assert len(results) > 0, "Should find Puma items"
        
        puma_count = sum(1 for r in results[:10] if 'puma' in r.filename.lower())
        if puma_count > 0:
            console.print(f"✓ Found {puma_count} Puma items", style="bold green")
    
    @pytest.mark.asyncio
    async def test_brand_search(self, search_engine):
        """Test 18: Search for various brands."""
        brands = ["Titan", "Skagen", "Fossil", "Fabindia"]
        
        for brand in brands:
            query = f"{brand} products"
            results = await search_engine.search_by_text(query, limit=5)
            
            brand_found = sum(1 for r in results if brand.lower() in r.filename.lower())
            console.print(f"\n{brand}: Found {brand_found} items in top 5 results", 
                         style="cyan" if brand_found > 0 else "yellow")
    
    # ========================================================================
    # GENDER-SPECIFIC TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_mens_apparel(self, search_engine):
        """Test 19: Search for men's apparel."""
        query = "men's clothing and accessories"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 19)
        
        assert len(results) > 0, "Should find men's items"
        
        mens_count = sum(1 for r in results[:10] if 'men' in r.filename.lower())
        console.print(f"✓ Found {mens_count} men's items")
    
    @pytest.mark.asyncio
    async def test_womens_apparel(self, search_engine):
        """Test 20: Search for women's apparel."""
        query = "women's fashion and accessories"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 20)
        
        assert len(results) > 0, "Should find women's items"
        
        womens_count = sum(1 for r in results[:10] if 'women' in r.filename.lower())
        console.print(f"✓ Found {womens_count} women's items")
    
    @pytest.mark.asyncio
    async def test_boys_items(self, search_engine):
        """Test 21: Search for boys' items."""
        query = "boys footwear and clothing"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 21)
        
        assert len(results) > 0, "Should find boys' items"
    
    # ========================================================================
    # SEMANTIC SIMILARITY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_semantic_shirts(self, search_engine):
        """Test 22: Semantic similarity for shirt queries."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 22: Semantic Similarity - Shirt Queries", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        query1 = "casual shirt for men"
        query2 = "men's everyday top wear"
        
        results1 = await search_engine.search_by_text(query1, limit=5)
        results2 = await search_engine.search_by_text(query2, limit=5)
        
        console.print(f"\n[bold]Query 1:[/bold] '{query1}'")
        for i, r in enumerate(results1[:3], 1):
            console.print(f"  {i}. {r.filename[:60]} (score: {r.score:.4f})")
        
        console.print(f"\n[bold]Query 2:[/bold] '{query2}'")
        for i, r in enumerate(results2[:3], 1):
            console.print(f"  {i}. {r.filename[:60]} (score: {r.score:.4f})")
        
        # Check overlap
        ids1 = {r.id for r in results1[:3]}
        ids2 = {r.id for r in results2[:3]}
        overlap = len(ids1 & ids2)
        
        console.print(f"\n✓ Result overlap: {overlap}/3 items", style="bold green")
    
    @pytest.mark.asyncio
    async def test_semantic_footwear(self, search_engine):
        """Test 23: Semantic similarity for footwear."""
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 23: Semantic Similarity - Footwear Queries", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        query1 = "comfortable shoes for walking"
        query2 = "casual footwear for daily use"
        
        results1 = await search_engine.search_by_text(query1, limit=5)
        results2 = await search_engine.search_by_text(query2, limit=5)
        
        assert len(results1) > 0 and len(results2) > 0, "Both queries should return results"
        
        console.print(f"\n[bold]Query 1:[/bold] '{query1}' - {len(results1)} results")
        console.print(f"[bold]Query 2:[/bold] '{query2}' - {len(results2)} results")
    
    # ========================================================================
    # COMPLEX QUERY TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_complex_multi_attribute(self, search_engine):
        """Test 24: Complex multi-attribute search."""
        query = "black casual shirt for summer"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 24)
        
        assert len(results) > 0, "Should handle complex queries"
        
        # Analyze how many attributes matched
        black_count = sum(1 for r in results[:5] if 'black' in r.filename.lower())
        shirt_count = sum(1 for r in results[:5] if 'shirt' in r.filename.lower())
        casual_count = sum(1 for r in results[:5] if 'casual' in r.filename.lower())
        summer_count = sum(1 for r in results[:5] if 'summer' in r.filename.lower())
        
        console.print(f"\n[bold]Attribute Match Analysis (Top 5):[/bold]")
        console.print(f"  Black color: {black_count}/5")
        console.print(f"  Shirts: {shirt_count}/5")
        console.print(f"  Casual style: {casual_count}/5")
        console.print(f"  Summer season: {summer_count}/5")
    
    @pytest.mark.asyncio
    async def test_outfit_combination(self, search_engine):
        """Test 25: Search for outfit combinations."""
        query = "complete outfit with shirt and pants"
        results = await search_engine.search_by_text(query, limit=10)
        
        self._display_results(query, results, 25)
        
        assert len(results) > 0, "Should find outfit components"
    
    # ========================================================================
    # COLLECTION STATS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_collection_stats(self, search_engine):
        """Test 26: Collection statistics."""
        stats = search_engine.get_collection_stats()
        
        console.print("\n" + "="*80, style="bold cyan")
        console.print("TEST 26: Fashion Collection Statistics", style="bold yellow")
        console.print("="*80, style="bold cyan")
        
        assert "collection_name" in stats
        assert "points_count" in stats
        assert stats["points_count"] > 0, "Collection should have points"
        
        panel = Panel(
            f"[bold]Collection:[/bold] {stats['collection_name']}\n"
            f"[bold]Total Products:[/bold] {stats['points_count']:,}\n"
            f"[bold]Vectors:[/bold] {stats['vectors_count']:,}\n"
            f"[bold]Indexed:[/bold] {stats.get('indexed_vectors_count', 0):,}\n"
            f"[bold]Status:[/bold] {stats['status']}",
            title="📊 Fashion Database Statistics",
            border_style="green"
        )
        console.print(panel)


# ============================================================================
# FASHION-SPECIFIC EXAMPLE QUERIES
# ============================================================================

FASHION_EXAMPLE_QUERIES = [
    # Apparel queries
    "red t-shirt for men",
    "women's purple formal shirt",
    "striped green ethnic shirt",
    "black track pants for workout",
    "casual denim jeans",
    
    # Accessory queries
    "silver watch for women",
    "leather belt black casual",
    "blue handbag for office",
    "pack of socks for sports",
    
    # Footwear queries
    "black casual shoes for men",
    "flip flops for summer",
    "sports shoes for running",
    "formal footwear brown",
    
    # Seasonal queries
    "summer casual wear",
    "winter accessories",
    "monsoon footwear",
    
    # Style queries
    "ethnic traditional wear",
    "casual everyday clothing",
    "formal office attire",
    "sportswear for gym",
    
    # Brand queries
    "Puma sports tshirt",
    "Titan watch collection",
    "Fabindia ethnic wear",
    
    # Color-specific
    "navy blue clothing",
    "grey apparel collection",
    "all black outfit",
    
    # Gender-specific
    "men's fashion accessories",
    "women's clothing collection",
    "boys footwear",
    
    # Complex queries
    "casual black shirt for summer",
    "formal watch for office",
    "comfortable footwear for daily use"
]


async def run_fashion_examples():
    """Run all fashion example queries."""
    config = Config.from_env()
    config.validate()
    engine = ImageSearchEngine(config)
    
    console.print("\n" + "="*80, style="bold magenta")
    console.print("FASHION DATASET - EXAMPLE SEARCH QUERIES", style="bold cyan")
    console.print("="*80, style="bold magenta")
    console.print(f"\nTotal queries to test: {len(FASHION_EXAMPLE_QUERIES)}\n")
    
    results_summary = []
    
    for i, query in enumerate(FASHION_EXAMPLE_QUERIES, 1):
        console.print(f"\n[{i}/{len(FASHION_EXAMPLE_QUERIES)}] [bold cyan]Searching:[/bold cyan] '{query}'")
        
        results = await engine.search_by_text(query, limit=3)
        
        if results:
            console.print(f"  [bold green]✓ Found {len(results)} results[/bold green]")
            for j, r in enumerate(results, 1):
                filename_display = r.filename[:55] + "..." if len(r.filename) > 55 else r.filename
                console.print(f"    {j}. {filename_display} [dim](score: {r.score:.4f})[/dim]")
            
            results_summary.append({
                "query": query,
                "count": len(results),
                "top_score": results[0].score
            })
        else:
            console.print("  [bold red]✗ No results found[/bold red]")
            results_summary.append({
                "query": query,
                "count": 0,
                "top_score": 0.0
            })
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.3)
    
    # Summary statistics
    console.print("\n" + "="*80, style="bold magenta")
    console.print("SUMMARY STATISTICS", style="bold yellow")
    console.print("="*80, style="bold magenta")
    
    successful = sum(1 for r in results_summary if r["count"] > 0)
    total = len(results_summary)
    avg_score = sum(r["top_score"] for r in results_summary if r["count"] > 0) / max(successful, 1)
    
    summary_panel = Panel(
        f"[bold]Total Queries:[/bold] {total}\n"
        f"[bold]Successful:[/bold] {successful} ({successful/total*100:.1f}%)\n"
        f"[bold]Failed:[/bold] {total - successful}\n"
        f"[bold]Average Top Score:[/bold] {avg_score:.4f}",
        title="🎯 Search Performance",
        border_style="green"
    )
    console.print(summary_panel)
    
    # Top performing queries
    top_queries = sorted(results_summary, key=lambda x: x["top_score"], reverse=True)[:5]
    
    console.print("\n[bold]Top 5 Best Matching Queries:[/bold]")
    for i, q in enumerate(top_queries, 1):
        console.print(f"  {i}. '{q['query']}' - Score: {q['top_score']:.4f}")


if __name__ == "__main__":
    """Run fashion search examples."""
    console.print(Panel.fit(
        "[bold magenta]Fashion & Clothing Dataset Search Testing[/bold magenta]\n"
        "Semantic search for apparel, accessories, and footwear",
        border_style="magenta"
    ))
    
    asyncio.run(run_fashion_examples())