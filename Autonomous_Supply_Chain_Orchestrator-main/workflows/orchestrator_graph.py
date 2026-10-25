from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END

from agents.market_intelligence import MarketIntelligenceAgent
from agents.inventory_logistics import InventoryLogisticsAgent
from agents.negotiation import NegotiationAgent
from agents.sustainability import SustainabilityAgent

# Lazy global instances
_market_agent = None
_inventory_agent = None
_negotiation_agent = None
_sustainability_agent = None

def get_market_agent():
    global _market_agent
    if not _market_agent:
        _market_agent = MarketIntelligenceAgent()
    return _market_agent

def get_inventory_agent():
    global _inventory_agent
    if not _inventory_agent:
        _inventory_agent = InventoryLogisticsAgent()
    return _inventory_agent

def get_negotiation_agent():
    global _negotiation_agent
    if not _negotiation_agent:
        _negotiation_agent = NegotiationAgent()
    return _negotiation_agent

def get_sustainability_agent():
    global _sustainability_agent
    if not _sustainability_agent:
        _sustainability_agent = SustainabilityAgent()
    return _sustainability_agent

class SupplyChainState(TypedDict):
    disruption_signal: str
    risk_assessment: str
    negotiation_plan: str
    audit_result: str
    reasoning_log: List[str]

def monitor_market(state: SupplyChainState):
    print("\n--- [Step 1] Market Intelligence: Scanning... ---")
    try:
        signal = get_market_agent().analyze_market()
    except Exception:
        print("None")
        signal = "None"
    print(f"Result: {signal}")
    return {"disruption_signal": signal, "reasoning_log": [f"Market Signal: {signal}"]}

def analyze_risk(state: SupplyChainState):
    print("\n--- [Step 2] Inventory & Logistics: Assessing Risk... ---")
    signal = state["disruption_signal"]
    if "NO_SIGNAL" in signal:
        return {"risk_assessment": "None", "reasoning_log": ["No risk detected."]}
    
    try:
        assessment = get_inventory_agent().assess_impact(signal)
    except Exception:
        print("None")
        assessment = "None"
    print(f"Result: {assessment}")
    return {"risk_assessment": assessment, "reasoning_log": [f"Risk Assessment: {assessment}"]}

def plan_response(state: SupplyChainState):
    print("\n--- [Step 3] Negotiation Agent: Planning Response... ---")
    risk = state["risk_assessment"]
    if risk == "None":
        return {"negotiation_plan": "None", "reasoning_log": ["No plan needed."]}
    
    try:
        plan = get_negotiation_agent().plan_response(risk)
    except Exception:
        print("None")
        plan = "None"
    print(f"Result: {plan}")
    return {"negotiation_plan": plan, "reasoning_log": [f"Draft Plan: {plan}"]}

def audit_plan(state: SupplyChainState):
    print("\n--- [Step 4] Sustainability Auditor: Validating... ---")
    plan = state["negotiation_plan"]
    if plan == "None":
        return {"audit_result": "Skipped", "reasoning_log": ["Audit skipped."]}
    
    try:
        audit = get_sustainability_agent().validate_plan(plan)
    except Exception:
        print("None")
        audit = "None"
    print(f"Result: {audit}")
    return {"audit_result": audit, "reasoning_log": [f"ESG Audit: {audit}"]}

def check_signal_condition(state: SupplyChainState):
    if "NO_SIGNAL" in state["disruption_signal"]:
        return "end"
    return "analyze"

from langgraph.checkpoint.memory import MemorySaver

def build_graph():
    workflow = StateGraph(SupplyChainState)

    workflow.add_node("market_intelligence", monitor_market)
    workflow.add_node("inventory_analysis", analyze_risk)
    workflow.add_node("negotiation_planning", plan_response)
    workflow.add_node("sustainability_audit", audit_plan)
    workflow.add_node("execute_action", lambda x: print("\n*** EXECUTING APPROVED PLAN ***"))

    workflow.set_entry_point("market_intelligence")

    workflow.add_conditional_edges(
        "market_intelligence",
        check_signal_condition,
        {
            "end": END,
            "analyze": "inventory_analysis"
        }
    )
    workflow.add_edge("inventory_analysis", "negotiation_planning")
    workflow.add_edge("negotiation_planning", "sustainability_audit")
    workflow.add_edge("sustainability_audit", "execute_action")

    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer, interrupt_before=["execute_action"])
    return app
