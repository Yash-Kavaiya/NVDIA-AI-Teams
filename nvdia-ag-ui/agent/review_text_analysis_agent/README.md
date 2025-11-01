# Review Text Analysis Agent

## Overview

The Review Text Analysis Agent is a specialized AI agent designed to analyze customer reviews from Walmart, extracting valuable insights, identifying common issues, and providing actionable intelligence for improving customer experience.

## Features

### 1. Sentiment Analysis
- Overall sentiment distribution (positive, neutral, negative)
- Sentiment breakdown by percentage
- Rating-based sentiment classification
- Trend identification

### 2. Issue Detection & Categorization
- Automatic identification of common customer complaints
- Issue categorization (delivery, customer service, product quality, etc.)
- Frequency analysis of issues
- Priority ranking based on impact

### 3. Keyword & Topic Analysis
- Search reviews by specific keywords
- Extract most frequently mentioned topics
- Identify emerging concerns
- Pattern recognition in customer feedback

### 4. Geographic Analysis
- Location-based review analysis
- Regional complaint patterns
- Geographic customer satisfaction comparison

### 5. Temporal Analysis
- Time-based review trends
- Date range filtering
- Seasonal pattern identification
- Historical progression tracking

### 6. Statistical Analysis
- Comprehensive review statistics
- Rating distributions
- Review length analysis
- Engagement metrics

## Data Structure

The agent works with Walmart customer review data containing:

```python
{
    "name": str,              # Customer name (anonymized)
    "location": str,          # City, State
    "Date": str,              # "Reviewed Month. Day, Year"
    "Rating": int,            # 1-5 stars
    "Review": str,            # Full review text
    "Image_Links": str        # Associated images (if any)
}
```

## Available Tools

### Core Analysis Tools

1. **`get_all_reviews()`**
   - Retrieves all customer reviews from the dataset
   - Returns: List of review dictionaries

2. **`get_reviews_by_rating(rating: int)`**
   - Filters reviews by star rating (1-5)
   - Args: rating (1-5)
   - Returns: List of matching reviews

3. **`get_reviews_by_location(location: str)`**
   - Finds reviews from a specific location
   - Args: location (e.g., "Phoenix, AZ")
   - Returns: List of reviews from that location

4. **`search_reviews_by_keyword(keyword: str)`**
   - Searches reviews containing specific keywords
   - Args: keyword or phrase
   - Returns: List of matching reviews

### Statistical Tools

5. **`get_review_statistics()`**
   - Comprehensive statistics about all reviews
   - Returns: Dictionary with:
     - Total review count
     - Rating distribution
     - Average rating
     - Reviews with images
     - Unique locations
     - Date range

6. **`get_sentiment_breakdown()`**
   - Sentiment analysis based on ratings
   - Returns: Dictionary with:
     - Negative count (Rating ≤ 2)
     - Neutral count (Rating = 3)
     - Positive count (Rating ≥ 4)
     - Percentages for each category

7. **`analyze_review_length()`**
   - Analyzes review length characteristics
   - Returns: Dictionary with:
     - Average characters
     - Average words
     - Shortest/longest reviews
     - Median length

### Advanced Analysis Tools

8. **`extract_common_issues()`**
   - Identifies and categorizes common issues
   - Returns: List of issues with:
     - Category name
     - Frequency count
     - Sorted by frequency

   Categories include:
   - Delivery
   - Customer service
   - Product quality
   - Refunds
   - Order issues
   - Account problems
   - Pricing
   - Third-party sellers

9. **`get_top_mentioned_topics(limit: int = 10)`**
   - Extracts most frequently mentioned topics
   - Args: limit (number of topics to return)
   - Returns: List of topics with frequency counts

10. **`get_reviews_by_date_range(start_date: str, end_date: str)`**
    - Filters reviews within a date range
    - Args: start_date, end_date (format: "Month Day, Year")
    - Returns: List of reviews in the date range

## Usage Examples

### Basic Sentiment Analysis
```python
# Get overall sentiment
sentiment = get_sentiment_breakdown()
print(f"Negative reviews: {sentiment['percentage_negative']:.1f}%")

# Get all 1-star reviews
negative_reviews = get_reviews_by_rating(1)
print(f"Found {len(negative_reviews)} extremely negative reviews")
```

### Issue Detection
```python
# Find common issues
issues = extract_common_issues()
for issue in issues[:3]:
    print(f"{issue['category']}: {issue['frequency']} mentions")

# Search for specific problems
delivery_issues = search_reviews_by_keyword("delivery")
print(f"Found {len(delivery_issues)} reviews mentioning delivery")
```

### Geographic Analysis
```python
# Analyze reviews by location
arizona_reviews = get_reviews_by_location("AZ")
texas_reviews = get_reviews_by_location("TX")

print(f"Arizona: {len(arizona_reviews)} reviews")
print(f"Texas: {len(texas_reviews)} reviews")
```

### Statistical Overview
```python
# Get comprehensive statistics
stats = get_review_statistics()
print(f"Total Reviews: {stats['total_reviews']}")
print(f"Average Rating: {stats['average_rating']:.2f}/5")
print(f"Rating Distribution: {stats['rating_distribution']}")
```

### Topic Analysis
```python
# Find top mentioned topics
topics = get_top_mentioned_topics(limit=5)
for topic in topics:
    print(f"{topic['topic']}: {topic['frequency']} mentions")
```

## Integration with NVIDIA AI

The agent is designed to work with NVIDIA's NIM (NVIDIA Inference Microservices) for enhanced text analysis capabilities:

### NVIDIA Embeddings Integration
```python
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

# Initialize embedder for semantic analysis
embedder = NVIDIAEmbeddings(model="NV-Embed-QA")

# Generate embeddings for review clustering or similarity search
review_embeddings = embedder.embed_documents([review['Review'] for review in reviews])
```

### NVIDIA Reranker for Better Results
```python
from langchain_nvidia_ai_endpoints import NVIDIARerank

# Initialize reranker for improved relevance
reranker = NVIDIARerank()

# Rerank search results based on query relevance
reranked_reviews = reranker.compress_documents(
    documents=initial_results,
    query="customer service problems"
)
```

## Agent Architecture

The Review Text Analysis Agent follows the SOLID principles:

### Single Responsibility
- Each tool has one specific purpose
- Clear separation between data loading, filtering, and analysis

### Dependency Injection
- Tools accept parameters rather than using global state
- Easy to test and maintain

### Interface Segregation
- Tools provide focused interfaces
- Users only call what they need

### Async-First (Future Enhancement)
- Ready for async operations when processing large datasets
- Supports concurrent analysis tasks

## Configuration

### Data Path
The agent looks for review data at:
```
review_data/Walmart_reviews_data.csv
```

### Required Dependencies
```txt
pandas>=2.0.0
google-adk>=0.1.0
langchain-nvidia-ai-endpoints>=0.1.0
```

## Use Cases

### Customer Experience Team
- Monitor overall customer satisfaction
- Identify urgent issues requiring attention
- Track sentiment trends over time
- Prioritize improvement initiatives

### Operations Team
- Analyze delivery and fulfillment issues
- Identify operational bottlenecks
- Monitor third-party seller performance
- Improve logistics and processes

### Customer Service Team
- Understand common customer complaints
- Identify training opportunities
- Improve response strategies
- Track resolution effectiveness

### Product Team
- Gather product quality feedback
- Identify feature requests
- Monitor product-specific issues
- Guide product improvements

### Marketing Team
- Understand customer perception
- Identify brand advocates and detractors
- Monitor competitive mentions
- Guide messaging and positioning

## Best Practices

1. **Start with Overview**: Always get statistics first to understand the dataset
2. **Drill Down**: Use broad queries first, then narrow with specific keywords
3. **Compare**: Look at multiple dimensions (time, location, rating)
4. **Validate**: Cross-reference findings with multiple tools
5. **Contextualize**: Always relate findings back to business impact

## Limitations

- Limited to structured CSV data
- Basic keyword matching (can be enhanced with NLP)
- Sentiment based on ratings (can be enhanced with text analysis)
- No real-time data updates
- English language only

## Future Enhancements

1. **Advanced NLP**: Integrate NVIDIA NeMo for deeper text understanding
2. **Real-time Processing**: Stream reviews as they come in
3. **Predictive Analytics**: Forecast trends and issues
4. **Multi-language Support**: Analyze reviews in multiple languages
5. **Image Analysis**: Analyze review images using NVIDIA Vision models
6. **Automated Alerts**: Notify teams of critical issues in real-time
7. **Integration**: Connect with CRM and support ticket systems

## Contributing

To add new analysis tools:

1. Add the function to `tools.py`
2. Update the agent's `tools` list in `agent.py`
3. Document the tool in this README
4. Add usage examples

## Support

For issues or questions:
- Check the agent's instructions in `agent.py`
- Review example queries in the agent description
- Ensure data path is correctly configured

## License

Part of the NVIDIA Retail AI Teams project.
