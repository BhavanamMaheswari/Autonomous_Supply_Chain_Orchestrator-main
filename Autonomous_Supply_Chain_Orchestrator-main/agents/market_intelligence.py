from core.llm import llm_fast
from core.config import NEWS_API_KEY
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests

class MarketIntelligenceAgent:
    """
    Role: The Eyes
    Model: llama3.2 (Fast monitoring)
    Function: Pulls news to detect disruptions.
    """
    def __init__(self):
        self.llm = llm_fast

    def fetch_news(self, query="supply chain disruption"):
        """Fetch news using NewsAPI."""
        if not NEWS_API_KEY:
            return "Error: NEWS_API_KEY not found."
        
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt&pageSize=5"
        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get("articles", [])
            headlines = [f"- {a['title']} ({a['source']['name']})" for a in articles]
            return "\n".join(headlines) if headlines else "No relevant news found."
        except Exception as e:
            return f"Error fetching news: {e}"

    def analyze_market(self):
        """
        Monitors market and returns a disruption signal if detailed.
        """
        news_data = self.fetch_news()
        
        prompt = ChatPromptTemplate.from_template(
            """
            You are the 'Market Intelligence' agent (The Eyes) of a supply chain orchestrator.
            Analyze the following news headlines for potential supply chain disruptions.
            
            News:
            {news_data}
            
            **INSTRUCTION FOR TESTING:**
            We are testing the system. Please find ANY potential negative angle or minor risk in the news (even if tenuous) and FLAG IT as a disruption.
            Do NOT output "NO_SIGNAL". You MUST find a signal.
            
            Output a concise alert formatted as:
            "SIGNAL_DETECTED: [Brief Description]"
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"news_data": news_data})
        return result
