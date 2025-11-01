"""
Test script for Inventory Agent

This script demonstrates how to test the inventory agent tools directly
without running the full ADK server.
"""

import sys
import os

# Add the parent directory to path to import tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inventory_agent import tools


def test_inventory_summary():
    """Test getting inventory summary"""
    print("\n" + "="*80)
    print("TEST: Inventory Summary")
    print("="*80)
    
    result = tools.get_inventory_summary()
    print(f"\nTotal Records: {result['total_records']:,}")
    print(f"Year Range: {result['year_range']}")
    print(f"Total Retail Sales: ${result['total_retail_sales']:,.2f}")
    print(f"Total Warehouse Sales: ${result['total_warehouse_sales']:,.2f}")
    print(f"Total Combined Sales: ${result['total_combined_sales']:,.2f}")
    print(f"Unique Suppliers: {result['unique_suppliers']:,}")
    print(f"Unique Items: {result['unique_items']:,}")
    
    print("\nItem Type Summary:")
    for item in result['item_type_summary'][:5]:
        print(f"  {item['ITEM TYPE']}: {item['UNIQUE ITEMS']} items, "
              f"${item['RETAIL SALES'] + item['WAREHOUSE SALES']:,.2f} total sales")


def test_wine_sales():
    """Test getting wine sales statistics"""
    print("\n" + "="*80)
    print("TEST: Wine Sales Analysis")
    print("="*80)
    
    result = tools.get_total_sales_by_item_type("WINE")
    print(f"\nItem Type: {result['item_type']}")
    print(f"Total Retail Sales: ${result['total_retail_sales']:,.2f}")
    print(f"Total Warehouse Sales: ${result['total_warehouse_sales']:,.2f}")
    print(f"Total Combined Sales: ${result['total_combined_sales']:,.2f}")
    print(f"Number of Records: {result['number_of_records']:,}")


def test_top_suppliers():
    """Test getting top suppliers"""
    print("\n" + "="*80)
    print("TEST: Top 5 Suppliers")
    print("="*80)
    
    result = tools.get_top_suppliers(limit=5)
    print(f"\nFilter: {result['item_type_filter']}")
    print("\nTop Suppliers:")
    for i, supplier in enumerate(result['top_suppliers'], 1):
        print(f"\n{i}. {supplier['SUPPLIER']}")
        print(f"   Total Sales: ${supplier['TOTAL_SALES']:,.2f}")
        print(f"   Retail: ${supplier['RETAIL SALES']:,.2f}")
        print(f"   Warehouse: ${supplier['WAREHOUSE SALES']:,.2f}")


def test_search_bourbon():
    """Test searching for bourbon items"""
    print("\n" + "="*80)
    print("TEST: Search for 'bourbon' items")
    print("="*80)
    
    result = tools.search_items_by_description("bourbon", limit=5)
    print(f"\nSearch Term: {result['search_term']}")
    print(f"Total Matches: {result['total_matches']}")
    print(f"Showing Top: {result['showing_top']}")
    
    print("\nTop Bourbon Items:")
    for i, item in enumerate(result['items'], 1):
        print(f"\n{i}. {item['ITEM DESCRIPTION']}")
        print(f"   Code: {item['ITEM CODE']}")
        print(f"   Type: {item['ITEM TYPE']}")
        print(f"   Supplier: {item['SUPPLIER']}")
        print(f"   Total Sales: ${item['TOTAL_SALES']:,.2f}")


def test_year_comparison():
    """Test comparing sales between years"""
    print("\n" + "="*80)
    print("TEST: Sales Comparison 2019 vs 2020")
    print("="*80)
    
    result_2019 = tools.get_sales_by_year_month(2019)
    result_2020 = tools.get_sales_by_year_month(2020)
    
    print("\n2019 Sales:")
    if 'error' not in result_2019:
        print(f"  Total Combined: ${result_2019['total_combined_sales']:,.2f}")
        print(f"  Transactions: {result_2019['number_of_transactions']:,}")
    else:
        print(f"  {result_2019['error']}")
    
    print("\n2020 Sales:")
    if 'error' not in result_2020:
        print(f"  Total Combined: ${result_2020['total_combined_sales']:,.2f}")
        print(f"  Transactions: {result_2020['number_of_transactions']:,}")
    else:
        print(f"  {result_2020['error']}")
    
    if 'error' not in result_2019 and 'error' not in result_2020:
        growth = ((result_2020['total_combined_sales'] - result_2019['total_combined_sales']) 
                  / result_2019['total_combined_sales'] * 100)
        print(f"\nYear-over-Year Growth: {growth:+.2f}%")


def test_item_details():
    """Test getting details for a specific item"""
    print("\n" + "="*80)
    print("TEST: Item Details for Code 10103")
    print("="*80)
    
    result = tools.get_item_details_by_code("10103")
    
    if 'error' not in result:
        print(f"\nItem Code: {result['item_code']}")
        print(f"Description: {result['item_description']}")
        print(f"Type: {result['item_type']}")
        print(f"Suppliers: {', '.join(result['suppliers'])}")
        print(f"\nTotal Retail Sales: ${result['total_retail_sales']:,.2f}")
        print(f"Total Warehouse Sales: ${result['total_warehouse_sales']:,.2f}")
        print(f"Total Combined Sales: ${result['total_combined_sales']:,.2f}")
        print(f"Total Transactions: {result['number_of_transactions']:,}")
        
        print("\nYearly Sales Breakdown:")
        for year_data in result['yearly_sales']:
            print(f"  {year_data['YEAR']}: ${year_data['RETAIL SALES'] + year_data['WAREHOUSE SALES']:,.2f}")
    else:
        print(f"\nError: {result['error']}")


def test_supplier_comparison():
    """Test comparing multiple suppliers"""
    print("\n" + "="*80)
    print("TEST: Compare JIM BEAM vs BACARDI")
    print("="*80)
    
    result = tools.compare_suppliers(["JIM BEAM", "BACARDI"])
    
    print(f"\nSuppliers Found: {result['suppliers_found']} / {result['suppliers_searched']}")
    
    for supplier_data in result['comparison']:
        print(f"\n{supplier_data['supplier_name']}:")
        print(f"  Total Sales: ${supplier_data['total_combined_sales']:,.2f}")
        print(f"  Unique Items: {supplier_data['unique_items']}")
        print(f"  Item Types:")
        for item_type in supplier_data['item_type_breakdown'][:3]:
            print(f"    {item_type['ITEM TYPE']}: "
                  f"${item_type['RETAIL SALES'] + item_type['WAREHOUSE SALES']:,.2f}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("INVENTORY AGENT TOOLS TEST SUITE")
    print("="*80)
    
    try:
        test_inventory_summary()
        test_wine_sales()
        test_top_suppliers()
        test_search_bourbon()
        test_year_comparison()
        test_item_details()
        test_supplier_comparison()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
