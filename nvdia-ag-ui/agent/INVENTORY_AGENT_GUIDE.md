# Inventory Agent - Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
cd nvdia-ag-ui/agent
pip install -r requirements.txt
```

2. **Verify data file exists:**
```bash
# The CSV should be at:
# NVDIA-Retail-AI-Teams/inventory_data/Warehouse_and_Retail_Sales.csv
```

## Running the Agent

### Option 1: ADK Web Interface (Recommended)

```bash
cd nvdia-ag-ui
adk web agent/inventory_agent
```

This will start an interactive web UI where you can chat with the agent.

### Option 2: Direct CLI Execution

```bash
cd nvdia-ag-ui
adk run agent/inventory_agent
```

This starts a command-line interface.

### Option 3: Test Tools Directly

```bash
cd nvdia-ag-ui/agent
python test_inventory_agent.py
```

This runs a comprehensive test suite showing all tool capabilities.

## Sample Queries

### Basic Sales Analysis

**Query:** "What are the total wine sales?"
```
The agent will use get_total_sales_by_item_type("WINE") and provide:
- Total retail sales: $X,XXX,XXX
- Total warehouse sales: $X,XXX,XXX
- Combined total: $X,XXX,XXX
- Number of wine transactions
```

**Query:** "Show me sales for January 2020"
```
The agent will use get_sales_by_year_month(2020, 1) and show:
- Breakdown by item type (Wine, Beer, Liquor, etc.)
- Total sales for the month
- Number of transactions
```

### Supplier Analysis

**Query:** "Who are the top 10 suppliers?"
```
The agent will use get_top_suppliers(limit=10) and rank them by:
- Total sales volume
- Retail vs warehouse breakdown
- Number of unique products
```

**Query:** "Compare JIM BEAM and DIAGEO"
```
The agent will use compare_suppliers(["JIM BEAM", "DIAGEO"]) and show:
- Side-by-side sales comparison
- Product mix (wine/beer/liquor breakdown)
- Unique item counts
```

### Product Search

**Query:** "Find all bourbon products"
```
The agent will use search_items_by_description("bourbon") and list:
- Top bourbon products by sales
- Item codes and descriptions
- Supplier information
- Sales figures
```

**Query:** "Tell me about item 10103"
```
The agent will use get_item_details_by_code("10103") and provide:
- Full product description
- All suppliers carrying this item
- Year-by-year sales history
- Total sales across all years
```

### Comparative Analysis

**Query:** "Compare wine sales between 2020 and 2021"
```
The agent will:
1. Get 2020 wine sales data
2. Get 2021 wine sales data
3. Calculate year-over-year growth
4. Highlight trends
```

**Query:** "What's the inventory overview?"
```
The agent will use get_inventory_summary() and show:
- Total number of records
- Year range of data
- Total sales across all categories
- Number of unique suppliers
- Number of unique products
- Breakdown by item type
```

## Understanding the Data

### Item Types
- **WINE**: All wine products
- **BEER**: Beer and cider products
- **LIQUOR**: Spirits (whiskey, vodka, rum, etc.)
- **KEGS**: Keg products
- **STR_SUPPLIES**: Store supplies

### Sales Columns
- **RETAIL SALES**: Direct sales to customers at retail locations
- **RETAIL TRANSFERS**: Internal transfers between retail stores
- **WAREHOUSE SALES**: Sales from warehouse/distribution center

### Time Period
- Data spans from 2020 onwards
- Monthly granularity (YEAR, MONTH columns)

## Advanced Usage Examples

### Multi-step Analysis

**Complex Query:** "Which wine suppliers had the highest growth from 2020 to 2021?"

The agent will:
1. Get top wine suppliers for 2020
2. Get top wine suppliers for 2021
3. Calculate growth rates for each
4. Rank by growth percentage
5. Provide insights

### Trend Analysis

**Complex Query:** "What are the seasonal trends for beer sales?"

The agent will:
1. Analyze beer sales by month across all years
2. Identify peak months
3. Calculate average monthly sales
4. Highlight seasonal patterns

## API Integration

### Using Tools Programmatically

```python
from inventory_agent import tools

# Get wine sales
wine_sales = tools.get_total_sales_by_item_type("WINE")
print(f"Total wine sales: ${wine_sales['total_combined_sales']:,.2f}")

# Find top suppliers
top_suppliers = tools.get_top_suppliers(limit=5, item_type="BEER")
for supplier in top_suppliers['top_suppliers']:
    print(f"{supplier['SUPPLIER']}: ${supplier['TOTAL_SALES']:,.2f}")

# Search products
bourbon_items = tools.search_items_by_description("bourbon", limit=10)
print(f"Found {bourbon_items['total_matches']} bourbon products")
```

## Troubleshooting

### Common Issues

**Problem:** Agent can't find the CSV file
```bash
# Check if file exists
ls inventory_data/Warehouse_and_Retail_Sales.csv

# If missing, ensure you're in the correct directory
cd NVDIA-Retail-AI-Teams
```

**Problem:** "No data found for item type"
```
Valid item types are:
- WINE
- BEER  
- LIQUOR
- KEGS
- STR_SUPPLIES

Item types are case-insensitive but must match exactly.
```

**Problem:** Search returns too many results
```
Use the limit parameter:
search_items_by_description("wine", limit=10)
```

**Problem:** Supplier name not found
```
Supplier names are case-insensitive and support partial matching.
Try searching with just part of the name:
- "JIM BEAM" → matches "JIM BEAM BRANDS CO"
- "DIAGEO" → matches "DIAGEO NORTH AMERICA INC"
```

## Performance Tips

1. **Use specific queries**: Instead of "tell me about everything", ask specific questions
2. **Limit results**: Use the limit parameter when expecting many results
3. **Filter by item type**: When analyzing suppliers, filter by item type for faster results
4. **Cache is automatic**: The CSV is loaded once and cached in memory

## Configuration

### Environment Variables

Create a `.env` file in `nvdia-ag-ui/agent/`:

```bash
# Google AI API Key (required)
GOOGLE_API_KEY=your_api_key_here

# Optional: Use Vertex AI instead of Google AI Studio
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### Getting API Keys

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## Integration with UI

The inventory agent can be integrated with the Next.js UI:

1. The agent is automatically discovered by the ADK system
2. Users can interact via the chat interface
3. Results are formatted in a user-friendly way
4. The agent maintains conversation context

## Best Practices

1. **Be Specific**: "What are wine sales in 2020?" is better than "Tell me about sales"
2. **Use Comparisons**: Ask for comparisons between periods, suppliers, or product types
3. **Request Insights**: Ask "What does this mean?" or "Why is this important?"
4. **Follow Up**: The agent maintains context, so follow-up questions work well
5. **Validate Results**: Double-check important numbers for business decisions

## Next Steps

- Explore the [README.md](./inventory_agent/README.md) for technical details
- Review [tools.py](./inventory_agent/tools.py) for available functions
- Check [agent.py](./inventory_agent/agent.py) for agent configuration
- Run [test_inventory_agent.py](./test_inventory_agent.py) to see all capabilities

## Support

For issues or questions:
1. Check the error message - it usually indicates what's wrong
2. Verify the CSV file is in the correct location
3. Ensure all dependencies are installed
4. Review the test output for expected behavior
