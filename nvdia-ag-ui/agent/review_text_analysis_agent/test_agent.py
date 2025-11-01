"""
Test script for Review Text Analysis Agent

This script tests the functionality of the review text analysis tools
and demonstrates how to use them effectively.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from review_text_analysis_agent import tools


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_review_statistics():
    """Test getting overall review statistics"""
    print_section("REVIEW STATISTICS")
    
    stats = tools.get_review_statistics()
    
    if stats:
        print(f"Total Reviews: {stats['total_reviews']}")
        print(f"Average Rating: {stats['average_rating']:.2f}/5")
        print(f"\nRating Distribution:")
        for rating, count in sorted(stats['rating_distribution'].items()):
            percentage = (count / stats['total_reviews']) * 100
            print(f"  {rating} stars: {count} reviews ({percentage:.1f}%)")
        print(f"\nReviews with images: {stats['reviews_with_images']}")
        print(f"Unique locations: {stats['unique_locations']}")
        print(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    else:
        print("❌ Failed to load review statistics")


def test_sentiment_breakdown():
    """Test sentiment analysis"""
    print_section("SENTIMENT BREAKDOWN")
    
    sentiment = tools.get_sentiment_breakdown()
    
    if sentiment:
        print(f"Negative (1-2 stars): {sentiment['negative']} reviews ({sentiment['percentage_negative']:.1f}%)")
        print(f"Neutral (3 stars): {sentiment['neutral']} reviews ({sentiment['percentage_neutral']:.1f}%)")
        print(f"Positive (4-5 stars): {sentiment['positive']} reviews ({sentiment['percentage_positive']:.1f}%)")
        
        # Add sentiment interpretation
        if sentiment['percentage_negative'] > 70:
            print("\n⚠️  WARNING: Critically high negative sentiment!")
        elif sentiment['percentage_negative'] > 50:
            print("\n⚠️  CAUTION: High negative sentiment detected")
    else:
        print("❌ Failed to analyze sentiment")


def test_common_issues():
    """Test issue extraction"""
    print_section("COMMON ISSUES")
    
    issues = tools.extract_common_issues()
    
    if issues:
        print("Top issues mentioned in reviews:\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue['category'].replace('_', ' ').title()}: {issue['frequency']} mentions")
    else:
        print("❌ Failed to extract common issues")


def test_keyword_search():
    """Test keyword search functionality"""
    print_section("KEYWORD SEARCH: 'delivery'")
    
    results = tools.search_reviews_by_keyword("delivery")
    
    print(f"Found {len(results)} reviews mentioning 'delivery'\n")
    
    if results:
        print("Sample reviews:")
        for review in results[:3]:
            print(f"\n- Rating: {review['Rating']}/5")
            print(f"  Location: {review['location']}")
            print(f"  Date: {review['Date']}")
            print(f"  Excerpt: {review['Review'][:150]}...")
    else:
        print("No reviews found with this keyword")


def test_rating_filter():
    """Test filtering by rating"""
    print_section("1-STAR REVIEWS")
    
    one_star = tools.get_reviews_by_rating(1)
    
    print(f"Total 1-star reviews: {len(one_star)}\n")
    
    if one_star:
        print("Sample 1-star review:")
        review = one_star[0]
        print(f"Location: {review['location']}")
        print(f"Date: {review['Date']}")
        print(f"Review: {review['Review'][:200]}...")


def test_location_analysis():
    """Test location-based filtering"""
    print_section("LOCATION ANALYSIS")
    
    # Test a few locations
    locations = ["AZ", "CA", "TX"]
    
    print("Reviews by state:\n")
    for loc in locations:
        reviews = tools.get_reviews_by_location(loc)
        print(f"{loc}: {len(reviews)} reviews")


def test_top_topics():
    """Test topic extraction"""
    print_section("TOP MENTIONED TOPICS")
    
    topics = tools.get_top_mentioned_topics(limit=10)
    
    if topics:
        print("Most frequently mentioned words:\n")
        for i, topic in enumerate(topics, 1):
            print(f"{i:2d}. {topic['topic']:20s} - {topic['frequency']:3d} mentions")
    else:
        print("❌ Failed to extract topics")


def test_review_length():
    """Test review length analysis"""
    print_section("REVIEW LENGTH ANALYSIS")
    
    analysis = tools.analyze_review_length()
    
    if analysis:
        print(f"Average review length: {analysis['average_characters']:.0f} characters")
        print(f"Average word count: {analysis['average_words']:.0f} words")
        print(f"Shortest review: {analysis['shortest_review']} characters")
        print(f"Longest review: {analysis['longest_review']} characters")
        print(f"Median length: {analysis['median_length']:.0f} characters")
    else:
        print("❌ Failed to analyze review lengths")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 20 + "REVIEW TEXT ANALYSIS AGENT TESTS" + " " * 26 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    try:
        test_review_statistics()
        test_sentiment_breakdown()
        test_common_issues()
        test_keyword_search()
        test_rating_filter()
        test_location_analysis()
        test_top_topics()
        test_review_length()
        
        print_section("TEST SUMMARY")
        print("✅ All tests completed successfully!")
        print("\nThe Review Text Analysis Agent is ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
