"""
Search the web for information (mock implementation).
"""

def search_web(query: str, num_results: int = 3) -> str:
    """
    Search the web for information (mock implementation).
    
    Args:
        query: Search query
        num_results: Number of results to return (1-10)
    
    Returns:
        Search results as formatted text
    """
    # This is a mock implementation
    # In real use, you would integrate with a search API like Google Custom Search
    
    mock_results = [
        {
            "title": f"Result about {query}",
            "url": f"https://example.com/search?q={query.replace(' ', '+')}",
            "snippet": f"This is a mock search result for '{query}'. In a real implementation, this would contain actual web search results."
        },
        {
            "title": f"More information on {query}",
            "url": f"https://wikipedia.org/search?q={query.replace(' ', '+')}",
            "snippet": f"Additional mock information about '{query}'. Real implementation would use APIs like Google Custom Search, Bing Search, or DuckDuckGo."
        },
        {
            "title": f"{query} - Latest Updates",
            "url": f"https://news.example.com/{query.replace(' ', '-')}",
            "snippet": f"Latest news and updates about '{query}'. This would contain real-time information from web sources."
        },
        {
            "title": f"Guide to {query}",
            "url": f"https://guide.example.com/{query.replace(' ', '-')}",
            "snippet": f"Comprehensive guide about '{query}' with detailed explanations and examples."
        },
        {
            "title": f"{query} - Community Discussion",
            "url": f"https://forum.example.com/topic/{query.replace(' ', '-')}",
            "snippet": f"Community discussions and expert opinions about '{query}'."
        }
    ]
    
    num_results = min(max(1, num_results), len(mock_results))
    results = mock_results[:num_results]
    
    formatted_results = f"Search results for '{query}':\n\n"
    for i, result in enumerate(results, 1):
        formatted_results += f"{i}. **{result['title']}**\n"
        formatted_results += f"   URL: {result['url']}\n"
        formatted_results += f"   {result['snippet']}\n\n"
    
    formatted_results += "Note: These are mock search results. For real web search, integrate with a search API service."
    
    return formatted_results
