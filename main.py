from workflows.orchestrator_graph import build_graph
import uuid

def main():
    print("Initializing Autonomous Supply Chain Orchestrator...")
    app = build_graph()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Starting Workflow (Thread: {thread_id})")
    
    # Run until interruption
    inputs = {"disruption_signal": "", "risk_assessment": "", "negotiation_plan": "", "audit_result": "", "reasoning_log": []}
    
    for event in app.stream(inputs, config=config):
        pass # Stream prints are handled inside nodes
        
    # Check current state
    state_snapshot = app.get_state(config)
    current_state = state_snapshot.values
    
    if "audit_result" in current_state:
        audit_status = current_state.get("audit_result", "Unknown")
        print("\n--- HUMAN INTERVENTION REQUIRED ---")
        print(f"Plan generated with status: {audit_status}")
        
        if "ESG_FLAGGED" in audit_status:
             print("WARNING: The plan has ESG violations. Review carefully.")
        else:
             print("Plan is approved and ready for execution.")

        print("Enter 'y' to execute, 'n' to abort.")
        
        user_input = input("Proceed? (y/n): ")
        if user_input.lower() == 'y':
            print("Resuming workflow...")
            # Resume execution
            for event in app.stream(None, config=config):
                print(event)
        else:
            print("Operation aborted by user.")
    else:
        # If it ended early (NO_SIGNAL)
        print("\nWorkflow completed or stopped by logic (No Signal).")

if __name__ == "__main__":
    main()
