"""
Inventory Agent Tools for Warehouse and Retail Sales Data Analysis

This module provides tools for querying and analyzing the inventory data
from the Warehouse_and_Retail_Sales.csv file.
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


# Load the CSV data once at module initialization
INVENTORY_DATA_PATH = os.path.join(
    os.path.dirname(__file__), 
    "..", 
    "..", 
    "..", 
    "inventory_data", 
    "Warehouse_and_Retail_Sales.csv"
)

# Global DataFrame to hold the inventory data
_inventory_df: Optional[pd.DataFrame] = None


def _load_inventory_data() -> pd.DataFrame:
    """Load and cache the inventory data."""
    global _inventory_df
    if _inventory_df is None:
        _inventory_df = pd.read_csv(INVENTORY_DATA_PATH)
        # Convert numeric columns to proper types
        _inventory_df['RETAIL SALES'] = pd.to_numeric(_inventory_df['RETAIL SALES'], errors='coerce')
        _inventory_df['RETAIL TRANSFERS'] = pd.to_numeric(_inventory_df['RETAIL TRANSFERS'], errors='coerce')
        _inventory_df['WAREHOUSE SALES'] = pd.to_numeric(_inventory_df['WAREHOUSE SALES'], errors='coerce')
    return _inventory_df


def get_total_sales_by_item_type(item_type: str) -> Dict[str, Any]:
    """
    Get total sales statistics for a specific item type (WINE, BEER, LIQUOR, etc.).
    
    Args:
        item_type: The type of item to analyze (e.g., 'WINE', 'BEER', 'LIQUOR')
        
    Returns:
        Dictionary containing total sales statistics for the item type
    """
    df = _load_inventory_data()
    
    # Filter by item type (case-insensitive)
    filtered_df = df[df['ITEM TYPE'].str.upper() == item_type.upper()]
    
    if filtered_df.empty:
        return {
            "item_type": item_type,
            "error": f"No data found for item type: {item_type}"
        }
    
    total_retail_sales = filtered_df['RETAIL SALES'].sum()
    total_retail_transfers = filtered_df['RETAIL TRANSFERS'].sum()
    total_warehouse_sales = filtered_df['WAREHOUSE SALES'].sum()
    
    return {
        "item_type": item_type,
        "total_retail_sales": round(total_retail_sales, 2),
        "total_retail_transfers": round(total_retail_transfers, 2),
        "total_warehouse_sales": round(total_warehouse_sales, 2),
        "total_combined_sales": round(total_retail_sales + total_warehouse_sales, 2),
        "number_of_records": len(filtered_df)
    }


def get_top_suppliers(limit: int = 10, item_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the top suppliers by total sales volume.
    
    Args:
        limit: Number of top suppliers to return (default: 10)
        item_type: Optional filter by item type
        
    Returns:
        Dictionary containing top suppliers and their sales data
    """
    df = _load_inventory_data()
    
    # Filter by item type if provided
    if item_type:
        df = df[df['ITEM TYPE'].str.upper() == item_type.upper()]
    
    # Calculate total sales per supplier
    supplier_sales = df.groupby('SUPPLIER').agg({
        'RETAIL SALES': 'sum',
        'RETAIL TRANSFERS': 'sum',
        'WAREHOUSE SALES': 'sum'
    }).reset_index()
    
    supplier_sales['TOTAL_SALES'] = (
        supplier_sales['RETAIL SALES'] + 
        supplier_sales['WAREHOUSE SALES']
    )
    
    # Sort by total sales and get top N
    top_suppliers = supplier_sales.nlargest(limit, 'TOTAL_SALES')
    
    return {
        "item_type_filter": item_type if item_type else "All types",
        "top_suppliers": top_suppliers.to_dict('records')
    }


def get_sales_by_year_month(year: int, month: Optional[int] = None) -> Dict[str, Any]:
    """
    Get sales statistics for a specific year and optionally month.
    
    Args:
        year: The year to analyze
        month: Optional month to filter (1-12)
        
    Returns:
        Dictionary containing sales statistics for the specified period
    """
    df = _load_inventory_data()
    
    # Filter by year
    filtered_df = df[df['YEAR'] == year]
    
    # Filter by month if provided
    if month:
        filtered_df = filtered_df[filtered_df['MONTH'] == month]
    
    if filtered_df.empty:
        return {
            "year": year,
            "month": month,
            "error": "No data found for specified period"
        }
    
    # Calculate statistics by item type
    item_type_stats = filtered_df.groupby('ITEM TYPE').agg({
        'RETAIL SALES': 'sum',
        'RETAIL TRANSFERS': 'sum',
        'WAREHOUSE SALES': 'sum'
    }).reset_index()
    
    total_retail = filtered_df['RETAIL SALES'].sum()
    total_warehouse = filtered_df['WAREHOUSE SALES'].sum()
    
    return {
        "year": year,
        "month": month if month else "All months",
        "total_retail_sales": round(total_retail, 2),
        "total_warehouse_sales": round(total_warehouse, 2),
        "total_combined_sales": round(total_retail + total_warehouse, 2),
        "sales_by_item_type": item_type_stats.to_dict('records'),
        "number_of_transactions": len(filtered_df)
    }


def search_items_by_description(search_term: str, limit: int = 20) -> Dict[str, Any]:
    """
    Search for items by description containing the search term.
    
    Args:
        search_term: The term to search for in item descriptions
        limit: Maximum number of results to return (default: 20)
        
    Returns:
        Dictionary containing matching items and their sales data
    """
    df = _load_inventory_data()
    
    # Search in item description (case-insensitive)
    filtered_df = df[
        df['ITEM DESCRIPTION'].str.contains(search_term, case=False, na=False)
    ]
    
    if filtered_df.empty:
        return {
            "search_term": search_term,
            "error": "No items found matching the search term"
        }
    
    # Get item statistics
    item_stats = filtered_df.groupby(['ITEM CODE', 'ITEM DESCRIPTION', 'ITEM TYPE']).agg({
        'RETAIL SALES': 'sum',
        'WAREHOUSE SALES': 'sum',
        'SUPPLIER': 'first'
    }).reset_index()
    
    item_stats['TOTAL_SALES'] = (
        item_stats['RETAIL SALES'] + 
        item_stats['WAREHOUSE SALES']
    )
    
    # Sort by total sales and limit results
    top_items = item_stats.nlargest(limit, 'TOTAL_SALES')
    
    return {
        "search_term": search_term,
        "total_matches": len(item_stats),
        "showing_top": min(limit, len(item_stats)),
        "items": top_items.to_dict('records')
    }


def get_item_details_by_code(item_code: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific item by its item code.
    
    Args:
        item_code: The item code to search for
        
    Returns:
        Dictionary containing detailed item information
    """
    df = _load_inventory_data()
    
    # Filter by item code
    filtered_df = df[df['ITEM CODE'].astype(str) == str(item_code)]
    
    if filtered_df.empty:
        return {
            "item_code": item_code,
            "error": "Item code not found"
        }
    
    # Get item description and type
    item_info = filtered_df.iloc[0]
    
    # Calculate sales statistics across all records
    total_retail = filtered_df['RETAIL SALES'].sum()
    total_warehouse = filtered_df['WAREHOUSE SALES'].sum()
    total_transfers = filtered_df['RETAIL TRANSFERS'].sum()
    
    # Get sales by year
    yearly_sales = filtered_df.groupby('YEAR').agg({
        'RETAIL SALES': 'sum',
        'WAREHOUSE SALES': 'sum',
        'RETAIL TRANSFERS': 'sum'
    }).reset_index()
    
    return {
        "item_code": item_code,
        "item_description": item_info['ITEM DESCRIPTION'],
        "item_type": item_info['ITEM TYPE'],
        "suppliers": filtered_df['SUPPLIER'].unique().tolist(),
        "total_retail_sales": round(total_retail, 2),
        "total_warehouse_sales": round(total_warehouse, 2),
        "total_retail_transfers": round(total_transfers, 2),
        "total_combined_sales": round(total_retail + total_warehouse, 2),
        "yearly_sales": yearly_sales.to_dict('records'),
        "number_of_transactions": len(filtered_df)
    }


def get_inventory_summary() -> Dict[str, Any]:
    """
    Get a high-level summary of the entire inventory dataset.
    
    Returns:
        Dictionary containing summary statistics of the inventory
    """
    df = _load_inventory_data()
    
    total_retail = df['RETAIL SALES'].sum()
    total_warehouse = df['WAREHOUSE SALES'].sum()
    total_transfers = df['RETAIL TRANSFERS'].sum()
    
    # Statistics by item type
    item_type_summary = df.groupby('ITEM TYPE').agg({
        'RETAIL SALES': 'sum',
        'WAREHOUSE SALES': 'sum',
        'ITEM CODE': 'nunique'
    }).reset_index()
    item_type_summary.columns = ['ITEM TYPE', 'RETAIL SALES', 'WAREHOUSE SALES', 'UNIQUE ITEMS']
    
    # Year range
    min_year = int(df['YEAR'].min())
    max_year = int(df['YEAR'].max())
    
    return {
        "total_records": len(df),
        "year_range": f"{min_year} - {max_year}",
        "total_retail_sales": round(total_retail, 2),
        "total_warehouse_sales": round(total_warehouse, 2),
        "total_retail_transfers": round(total_transfers, 2),
        "total_combined_sales": round(total_retail + total_warehouse, 2),
        "unique_suppliers": df['SUPPLIER'].nunique(),
        "unique_items": df['ITEM CODE'].nunique(),
        "item_type_summary": item_type_summary.to_dict('records')
    }


def compare_suppliers(supplier_names: List[str]) -> Dict[str, Any]:
    """
    Compare sales performance between multiple suppliers.
    
    Args:
        supplier_names: List of supplier names to compare
        
    Returns:
        Dictionary containing comparative statistics for the suppliers
    """
    df = _load_inventory_data()
    
    comparison_results = []
    
    for supplier in supplier_names:
        # Case-insensitive partial match
        supplier_df = df[
            df['SUPPLIER'].str.contains(supplier, case=False, na=False)
        ]
        
        if not supplier_df.empty:
            actual_supplier_name = supplier_df['SUPPLIER'].iloc[0]
            total_retail = supplier_df['RETAIL SALES'].sum()
            total_warehouse = supplier_df['WAREHOUSE SALES'].sum()
            
            # Get item type breakdown
            item_types = supplier_df.groupby('ITEM TYPE').agg({
                'RETAIL SALES': 'sum',
                'WAREHOUSE SALES': 'sum'
            }).reset_index()
            
            comparison_results.append({
                "supplier_name": actual_supplier_name,
                "total_retail_sales": round(total_retail, 2),
                "total_warehouse_sales": round(total_warehouse, 2),
                "total_combined_sales": round(total_retail + total_warehouse, 2),
                "unique_items": supplier_df['ITEM CODE'].nunique(),
                "item_type_breakdown": item_types.to_dict('records')
            })
    
    return {
        "comparison": comparison_results,
        "suppliers_found": len(comparison_results),
        "suppliers_searched": len(supplier_names)
    }
