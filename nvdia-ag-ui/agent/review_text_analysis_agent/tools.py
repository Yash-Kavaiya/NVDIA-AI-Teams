"""
Review Text Analysis Tools for Walmart Customer Reviews

This module provides tools for analyzing customer reviews using NVIDIA NIM models
and CSV-based review data.
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime
import re

# Path to the review data CSV
# Get the root directory of the project (5 levels up from this file)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
REVIEW_DATA_PATH = os.path.join(PROJECT_ROOT, "review_data", "Walmart_reviews_data.csv")


def load_review_data() -> pd.DataFrame:
    """Load the Walmart reviews dataset"""
    try:
        df = pd.read_csv(REVIEW_DATA_PATH)
        return df
    except Exception as e:
        print(f"Error loading review data: {e}")
        return pd.DataFrame()


def get_all_reviews() -> List[Dict[str, Any]]:
    """
    Retrieve all customer reviews from the dataset.
    
    Returns:
        List of dictionaries containing review information
    """
    df = load_review_data()
    if df.empty:
        return []
    
    reviews = df.to_dict('records')
    return reviews


def get_reviews_by_rating(rating: int) -> List[Dict[str, Any]]:
    """
    Get all reviews with a specific rating.
    
    Args:
        rating: Star rating (1-5)
        
    Returns:
        List of reviews with the specified rating
    """
    df = load_review_data()
    if df.empty:
        return []
    
    filtered = df[df['Rating'] == rating]
    return filtered.to_dict('records')


def get_reviews_by_location(location: str) -> List[Dict[str, Any]]:
    """
    Get all reviews from a specific location.
    
    Args:
        location: Location string (e.g., "Phoenix, AZ")
        
    Returns:
        List of reviews from the specified location
    """
    df = load_review_data()
    if df.empty:
        return []
    
    # Case-insensitive partial match
    filtered = df[df['location'].str.contains(location, case=False, na=False)]
    return filtered.to_dict('records')


def search_reviews_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    """
    Search for reviews containing a specific keyword or phrase.
    
    Args:
        keyword: The keyword or phrase to search for in review text
        
    Returns:
        List of reviews containing the keyword
    """
    df = load_review_data()
    if df.empty:
        return []
    
    # Case-insensitive search in review text
    filtered = df[df['Review'].str.contains(keyword, case=False, na=False)]
    return filtered.to_dict('records')


def get_review_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about all reviews.
    
    Returns:
        Dictionary containing review statistics
    """
    df = load_review_data()
    if df.empty:
        return {}
    
    stats = {
        'total_reviews': len(df),
        'rating_distribution': df['Rating'].value_counts().to_dict(),
        'average_rating': float(df['Rating'].mean()),
        'reviews_with_images': len(df[df['Image_Links'] != "['No Images']"]),
        'unique_locations': df['location'].nunique(),
        'date_range': {
            'earliest': df['Date'].min(),
            'latest': df['Date'].max()
        }
    }
    
    return stats


def extract_common_issues() -> List[Dict[str, Any]]:
    """
    Extract and categorize common issues mentioned in reviews.
    
    Returns:
        List of common issues with frequency counts
    """
    df = load_review_data()
    if df.empty:
        return []
    
    # Common issue keywords
    issue_keywords = {
        'delivery': ['delivery', 'delivered', 'shipping', 'shipped', 'arrive', 'arrived'],
        'customer_service': ['customer service', 'representative', 'support', 'agent'],
        'product_quality': ['quality', 'defective', 'broken', 'damaged', 'fake', 'scam'],
        'refund': ['refund', 'return', 'money back', 'charged'],
        'order_issues': ['order', 'missing', 'wrong', 'incorrect'],
        'account': ['account', 'login', 'password', 'locked'],
        'pricing': ['price', 'overcharged', 'expensive', 'cheap'],
        'third_party': ['third party', 'seller', 'marketplace']
    }
    
    issues_found = {}
    
    for category, keywords in issue_keywords.items():
        count = 0
        for keyword in keywords:
            count += df['Review'].str.contains(keyword, case=False, na=False).sum()
        if count > 0:
            issues_found[category] = count
    
    # Sort by frequency
    sorted_issues = [
        {'category': k, 'frequency': v} 
        for k, v in sorted(issues_found.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return sorted_issues


def get_sentiment_breakdown() -> Dict[str, Any]:
    """
    Get a simple sentiment breakdown based on ratings.
    
    Returns:
        Dictionary with sentiment categories and counts
    """
    df = load_review_data()
    if df.empty:
        return {}
    
    sentiment_breakdown = {
        'negative': len(df[df['Rating'] <= 2]),
        'neutral': len(df[df['Rating'] == 3]),
        'positive': len(df[df['Rating'] >= 4]),
        'percentage_negative': (len(df[df['Rating'] <= 2]) / len(df) * 100),
        'percentage_neutral': (len(df[df['Rating'] == 3]) / len(df) * 100),
        'percentage_positive': (len(df[df['Rating'] >= 4]) / len(df) * 100)
    }
    
    return sentiment_breakdown


def get_reviews_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Get reviews within a specific date range.
    
    Args:
        start_date: Start date in format "Month Day, Year" (e.g., "July 1, 2023")
        end_date: End date in format "Month Day, Year"
        
    Returns:
        List of reviews in the date range
    """
    df = load_review_data()
    if df.empty:
        return []
    
    # Extract dates from the "Reviewed Month. Day, Year" format
    df['parsed_date'] = df['Date'].str.extract(r'Reviewed (.+)')[0]
    
    # Filter by date range (string comparison works for this format)
    filtered = df[
        (df['parsed_date'] >= start_date) & 
        (df['parsed_date'] <= end_date)
    ]
    
    return filtered.to_dict('records')


def analyze_review_length() -> Dict[str, Any]:
    """
    Analyze the length characteristics of reviews.
    
    Returns:
        Dictionary with review length statistics
    """
    df = load_review_data()
    if df.empty:
        return {}
    
    df['review_length'] = df['Review'].str.len()
    df['word_count'] = df['Review'].str.split().str.len()
    
    analysis = {
        'average_characters': float(df['review_length'].mean()),
        'average_words': float(df['word_count'].mean()),
        'shortest_review': int(df['review_length'].min()),
        'longest_review': int(df['review_length'].max()),
        'median_length': float(df['review_length'].median())
    }
    
    return analysis


def get_top_mentioned_topics(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Extract the most frequently mentioned topics across all reviews.
    
    Args:
        limit: Number of top topics to return
        
    Returns:
        List of top topics with frequency counts
    """
    df = load_review_data()
    if df.empty:
        return []
    
    # Combine all reviews
    all_text = ' '.join(df['Review'].dropna().values)
    
    # Extract common business-related terms (simple word frequency)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
    
    # Filter out common stop words
    stop_words = {'that', 'this', 'have', 'with', 'from', 'they', 'them', 
                  'were', 'been', 'would', 'said', 'there', 'their', 'which',
                  'also', 'about', 'when', 'just', 'very', 'even', 'than'}
    
    filtered_words = [w for w in words if w not in stop_words]
    
    # Count frequencies
    word_freq = Counter(filtered_words)
    
    top_topics = [
        {'topic': word, 'frequency': count} 
        for word, count in word_freq.most_common(limit)
    ]
    
    return top_topics
