# Inventory Agent

An intelligent AI agent built with Google ADK for analyzing warehouse and retail sales data.

## Overview

The Inventory Agent provides comprehensive analysis of retail and warehouse sales data, including:
- Wine, Beer, Liquor, and other product categories
- Supplier performance comparison
- Time-based sales analysis
- Product search and detailed item information

## Architecture

```
inventory_agent/
├── __init__.py          # Package initialization
├── agent.py             # Main agent definition with Google ADK
├── tools.py             # Data analysis tools/functions
└── README.md            # This file
```

## Data Source

The agent analyzes data from `inventory_data/Warehouse_and_Retail_Sales.csv` containing:
- **Time Period**: Year and Month
- **Supplier Information**: Company names
- **Product Details**: Item codes, descriptions, types
- **Sales Data**: Retail sales, retail transfers, warehouse sales

### Data Schema
| Column | Type | Description |
|--------|------|-------------|
| YEAR | Integer | Sales year |
| MONTH | Integer | Sales month (1-12) |
| SUPPLIER | String | Supplier company name |
| ITEM CODE | String | Unique product identifier |
| ITEM DESCRIPTION | String | Product name and size |
| ITEM TYPE | String | Category (WINE, BEER, LIQUOR, KEGS, STR_SUPPLIES) |
| RETAIL SALES | Float | Direct retail sales amount |
| RETAIL TRANSFERS | Float | Transfers between retail locations |
| WAREHOUSE SALES | Float | Sales from warehouse |

## Available Tools

### 1. `get_total_sales_by_item_type(item_type: str)`
Get total sales statistics for a specific product category.

**Example:**
```python
get_total_sales_by_item_type("WINE")
```

**Returns:**
```json
{
  "item_type": "WINE",
  "total_retail_sales": 150000.00,
  "total_retail_transfers": 5000.00,
  "total_warehouse_sales": 75000.00,
  "total_combined_sales": 225000.00,
  "number_of_records": 50000
}
```

### 2. `get_top_suppliers(limit: int, item_type: Optional[str])`
Get top suppliers by sales volume with optional filtering by item type.

**Example:**
```python
get_top_suppliers(limit=10, item_type="BEER")
```

### 3. `get_sales_by_year_month(year: int, month: Optional[int])`
Analyze sales for a specific time period.

**Example:**
```python
get_sales_by_year_month(2020, 6)  # June 2020
get_sales_by_year_month(2021)     # All of 2021
```

### 4. `search_items_by_description(search_term: str, limit: int)`
Search for products by description.

**Example:**
```python
search_items_by_description("bourbon", limit=20)
```

### 5. `get_item_details_by_code(item_code: str)`
Get comprehensive information about a specific product.

**Example:**
```python
get_item_details_by_code("10103")
```

### 6. `get_inventory_summary()`
Get high-level overview of entire dataset.

**Example:**
```python
get_inventory_summary()
```

### 7. `compare_suppliers(supplier_names: List[str])`
Compare performance between multiple suppliers.

**Example:**
```python
compare_suppliers(["JIM BEAM", "BACARDI", "DIAGEO"])
```

## Usage

### Running the Agent

```bash
# Start ADK web interface
cd nvdia-ag-ui
adk web agent/inventory_agent

# Or run directly
adk run agent/inventory_agent
```

### Example Queries

1. **Sales Analysis**
   - "What are the total wine sales in the dataset?"
   - "Show me beer sales for 2020"
   - "Compare liquor sales between 2020 and 2021"

2. **Supplier Analysis**
   - "Who are the top 10 suppliers?"
   - "Which suppliers provide the most wine products?"
   - "Compare JIM BEAM and BACARDI performance"

3. **Product Search**
   - "Find all bourbon products"
   - "Show me items from Knob Creek"
   - "What vodka products are available?"

4. **Item Details**
   - "Get details for item code 10103"
   - "Tell me about Grey Goose sales"

5. **Inventory Overview**
   - "Give me a summary of the inventory"
   - "What item types do we have?"
   - "How many unique products are in the database?"

## Technical Details

### Design Principles

Following Google ADK best practices:
- **Single Responsibility**: Each tool function has one clear purpose
- **Type Safety**: Full type hints with Python typing
- **Error Handling**: Graceful handling of missing/invalid data
- **Efficient Data Loading**: CSV loaded once and cached globally
- **Clean Responses**: Structured dictionaries for easy consumption

### Dependencies

```python
pandas>=2.0.0  # Data manipulation and analysis
```

### Integration with Google ADK

The agent is defined using Google's Agent Development Kit (ADK):

```python
from google.adk.agents import Agent

root_agent = Agent(
    name='inventory_agent',
    model='gemini-2.0-flash',
    description='...',
    instruction='...',
    tools=[...]
)
```

### Data Processing

- **Lazy Loading**: CSV is loaded only when first tool is called
- **Type Conversion**: Numeric columns properly converted for calculations
- **Caching**: DataFrame cached in memory for fast repeated queries
- **Case-Insensitive Search**: User-friendly text searches

## Future Enhancements

Potential improvements:
- [ ] Add sales forecasting capabilities
- [ ] Implement trend analysis and seasonality detection
- [ ] Add data visualization generation
- [ ] Support for filtering by date ranges
- [ ] Integration with real-time inventory systems
- [ ] Export capabilities (Excel, PDF reports)

## Troubleshooting

### Common Issues

**Problem**: "No data found for item type"
- **Solution**: Check item type spelling (WINE, BEER, LIQUOR, KEGS, STR_SUPPLIES)
- Item types are case-insensitive but must match available types

**Problem**: "Item code not found"
- **Solution**: Use `search_items_by_description()` first to find the correct item code

**Problem**: CSV not loading
- **Solution**: Ensure `inventory_data/Warehouse_and_Retail_Sales.csv` exists at correct path

## Contributing

When adding new tools:
1. Define function in `tools.py` with proper type hints
2. Add comprehensive docstring
3. Handle errors gracefully
4. Return structured dictionary
5. Add function to agent's `tools` list in `agent.py`
6. Update this README

## License

Part of the NVIDIA Retail AI Teams project.
