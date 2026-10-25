from core.llm import llm_reasoning
from core.memory import MemoryModule
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class NegotiationAgent:
    """
    Role: The Voice
    Model: deepseek-r1 (Complex reasoning)
    Function: Formulates supplier emails/messages based on historical solutions.
    """
    def __init__(self):
        self.llm = llm_reasoning
        self.memory = MemoryModule()

    def plan_response(self, risk_assessment):
        """
        Formulates a negotiation strategy.
        """
        # Step 1: Retrieve Context
        # We assume risk_assessment has keywords we can query.
        # For prototype, we just query generic "supply chain disruption solutions"
        context_docs = self.memory.retrieve_context("supply chain delay disruption solutions")
        context_text = "\n".join(context_docs)

        # Step 2: Reasoning with DeepSeek-R1
        prompt = ChatPromptTemplate.from_template(
            """
            You are the 'Negotiation Agent' (The Voice).
            Task: Formulate a strategy and draft a supplier email to mitigate the following risk.
            
            Risk Assessment:
            {risk_assessment}
            
            Historical Solutions (Memory):
            {context}
            
            CRITICAL INSTRUCTIONS FOR APPROVAL:
            The Sustainability Auditor will REJECT your plan if it is vague. You must EXPLICITLY detail your strategy for:
            1. Carbon-Neutral Logistics (e.g., EV fleets, rail).
            2. Fair Labor Compliance (e.g., supplier audits, wage guarantees).
            3. Waste Minimization (e.g., circular economy, reduced packaging).
            
            Do not just mention these; explain HOW you will achieve them.
            
            Output your reasoning process first (if your model supports it), followed by the Final Plan and Email Draft.
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"risk_assessment": risk_assessment, "context": context_text})
