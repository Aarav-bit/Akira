"""
Web Search Module - DuckDuckGo search integration
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WebSearch:
    def __init__(self):
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("duckduckgo-search not installed")
    
    def search(self, query: str, max_results: int = 3) -> str:
        """Search the web and return summarized results"""
        if not self.available:
            return "Web search is not available."
        
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            if not results:
                return f"No results found for '{query}'."
            
            # Format results concisely
            summary = []
            for i, r in enumerate(results[:3], 1):
                title = r.get('title', '')
                body = r.get('body', '')[:150]
                summary.append(f"{i}. {title}: {body}")
            
            return " ".join(summary)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return "Sorry, I couldn't complete the search."
    
    def get_weather(self, location: str) -> str:
        """Get weather for a location"""
        return self.search(f"weather in {location} today")
    
    def get_news(self, topic: str = "latest") -> str:
        """Get news headlines"""
        try:
            results = list(self.ddgs.news(topic, max_results=3))
            
            if not results:
                return "No news found."
            
            headlines = []
            for r in results[:3]:
                title = r.get('title', '')
                headlines.append(title)
            
            return "Top headlines: " + ". ".join(headlines)
            
        except Exception as e:
            logger.error(f"News error: {e}")
            return self.search(f"{topic} news today")
    
    def instant_answer(self, query: str) -> Optional[str]:
        """Try to get instant answer"""
        try:
            results = list(self.ddgs.answers(query))
            if results:
                return results[0].get('text', '')[:300]
            return None
        except:
            return None
