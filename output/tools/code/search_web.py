"""
Search the web for information (mock implementation).
"""

import json

def search_web(query: str, num_results: int = 3) -> str:
    """
    Search the web for information (mock implementation).
    
    Args:
        query: Search query
        num_results: Number of results to return (1-10)
    
    Returns:
        search_results (array[object]): List of search result objects with title, URL, and snippet (json format)
        formatted_results (string): Human-readable formatted search results (markdown format)
        query_processed (string): The processed search query (plain_text format)
        result_count (integer): Number of results returned
    """
    try:
        # This is a mock implementation
        # In real use, you would integrate with a search API like Google Custom Search
        
        processed_query = query.strip()
        
        mock_results = [
            {
                "title": f"Result about {processed_query}",
                "url": f"https://example.com/search?q={processed_query.replace(' ', '+')}",
                "snippet": f"This is a mock search result for '{processed_query}'. In a real implementation, this would contain actual web search results."
            },
            {
                "title": f"More information on {processed_query}",
                "url": f"https://wikipedia.org/search?q={processed_query.replace(' ', '+')}",
                "snippet": f"Additional mock information about '{processed_query}'. Real implementation would use APIs like Google Custom Search, Bing Search, or DuckDuckGo."
            },
            {
                "title": f"{processed_query} - Latest Updates",
                "url": f"https://news.example.com/{processed_query.replace(' ', '-')}",
                "snippet": f"Latest news and updates about '{processed_query}'. This would contain real-time information from web sources."
            },
            {
                "title": f"Guide to {processed_query}",
                "url": f"https://guide.example.com/{processed_query.replace(' ', '-')}",
                "snippet": f"Comprehensive guide about '{processed_query}' with detailed explanations and examples."
            },
            {
                "title": f"{processed_query} - Community Discussion",
                "url": f"https://forum.example.com/topic/{processed_query.replace(' ', '-')}",
                "snippet": f"Community discussions and expert opinions about '{processed_query}'."
            }
        ]
        
        num_results = min(max(1, num_results), len(mock_results))
        search_results = mock_results[:num_results]
        
        # Generate markdown formatted results
        formatted_results = f"# Search Results for '{processed_query}'\n\n"
        for i, result in enumerate(search_results, 1):
            formatted_results += f"## {i}. {result['title']}\n\n"
            formatted_results += f"**URL:** {result['url']}\n\n"
            formatted_results += f"{result['snippet']}\n\n"
            formatted_results += "---\n\n"
        
        formatted_results += "*Note: These are mock search results. For real web search, integrate with a search API service.*"
        
        result = {
            "search_results": search_results,
            "formatted_results": formatted_results,
            "query_processed": processed_query,
            "result_count": len(search_results)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "search_results": [],
            "formatted_results": f"# Search Error\n\nError searching for '{query}': {str(e)}",
            "query_processed": query,
            "result_count": 0
        }
        return json.dumps(error_result, indent=2)
