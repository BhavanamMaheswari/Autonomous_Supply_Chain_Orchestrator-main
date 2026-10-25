import pandas as pd
from core.llm import llm_tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class InventoryLogisticsAgent:
    """
    Role: The Hands
    Model: mistral (Reliable tool use)
    Function: Interfaces with ERP/CSV to track 'At Risk' stock.
    """
    def __init__(self, csv_path="data/inventory.csv"):
        self.csv_path = csv_path
        self.llm = llm_tool

    def check_inventory(self, query_region_or_product):
        """
        Reads the CSV and filters for items related to the query.
        """
        try:
            df = pd.read_csv(self.csv_path)
            # Simple string matching for prototype
            # In real world, use pandas filtering or SQL
            relevant_items = df[
                df.apply(lambda row: row.astype(str).str.contains(query_region_or_product, case=False, regex=False).any(), axis=1)
            ]
            
            if relevant_items.empty:
                return "No matching inventory found."
            
            return relevant_items.to_markdown(index=False)
        except Exception as e:
            return f"Error reading inventory: {e}"

    def assess_impact(self, disruption_signal):
        """
        Determines which inventory is at risk based on the disruption signal.
        """
        # Step 1: Use LLM to extract key locations/products from signal
        extraction_prompt = ChatPromptTemplate.from_template(
            "Extract the key location or product category from this disruption signal: {signal}. Output ONLY the keyword."
        )
        chain = extraction_prompt | self.llm | StrOutputParser()
        keyword = chain.invoke({"signal": disruption_signal}).strip()
        
        # Step 2: Query Inventory
        inventory_data = self.check_inventory(keyword)
        
        # Step 3: Summarize Risk
        analysis_prompt = ChatPromptTemplate.from_template(
            """
            You are the 'Inventory & Logistics' agent (The Hands).
            Based on the disruption '{signal}' and the following inventory data:
            
            {inventory_data}
            
            Quantify the risk. Output a summary like:
            "RISK_ASSESSMENT: [X]% of [Product] at risk due to [Reason]. Total value at stake: [Amount]."
            """
        )
        
        chain = analysis_prompt | self.llm | StrOutputParser()
        return chain.invoke({"signal": disruption_signal, "inventory_data": inventory_data})
