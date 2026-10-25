from core.llm import llm_fast
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class SustainabilityAgent:
    """
    Role: The Conscience
    Model: llama3.2 (Logic verification)
    Function: Validates paths against local ESG guidelines.
    """
    def __init__(self):
        self.llm = llm_fast

    def validate_plan(self, negotiation_plan):
        """
        Audits the proposed plan for ESG compliance.
        """
        prompt = ChatPromptTemplate.from_template(
            """
            You are the 'Sustainability Auditor' (The Conscience).
            Review the following negotiation plan for ESG (Environmental, Social, and Governance) compliance.
            
            Plan:
            {negotiation_plan}
            
            Guidelines:
            - Prioritize carbon-neutral routes.
            - Ensure fair labor practices in supplier choice (if mentioned).
            - Minimizing waste.
            
            Result:
            - If approved, output "ESG_APPROVED" followed by a brief reason.
            - If rejected, output "ESG_FLAGGED" followed by the violation and recommendation.
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"negotiation_plan": negotiation_plan})
