
import sys
import os
import time
import threading
import subprocess
import uuid
import psutil
from unittest.mock import MagicMock

# Add current dir to path
sys.path.append(os.getcwd())

# --- 1. Setup Resource Monitoring ---
vram_log = []
ram_log = []
stop_monitoring = threading.Event()

def monitor_resources():
    process = psutil.Process()
    while not stop_monitoring.is_set():
        timestamp = time.time()
        
        # VRAM (Nvidia)
        try:
            cmd = "nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits"
            res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if res.returncode == 0:
                mem_used = int(res.stdout.strip())
                vram_log.append((timestamp, mem_used))
        except Exception:
            pass
            
        # RAM (System wide used or just process? User asked for VRAM/RAM Usage. 
        # Since Ollama is external, tracking system wide RAM change might be noisy but better than just python process)
        try:
            ram_gb = psutil.virtual_memory().used / (1024 ** 3)
            ram_log.append((timestamp, ram_gb))
        except:
            pass
            
        time.sleep(0.1)

monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
monitor_thread.start()

# --- 2. Setup Callbacks ---
from langchain_core.callbacks import BaseCallbackHandler

execution_log = []

class DiagnosticHandler(BaseCallbackHandler):
    def __init__(self, model_alias, actual_model_name):
        self.model_alias = model_alias
        self.actual_model_name = actual_model_name
        self.start_time = None
        self.first_token_time = None
        self.end_time = None
        self.tokens = 0
        
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        self.first_token_time = None
        self.tokens = 0
        print(f"[{self.model_alias}] Request sent...")
        
    def on_llm_new_token(self, token, **kwargs):
        if self.first_token_time is None:
            self.first_token_time = time.time()
            print(f"[{self.model_alias}] First token received (TTFT: {self.first_token_time - self.start_time:.2f}s)")
        self.tokens += 1
        
    def on_llm_end(self, response, **kwargs):
        self.end_time = time.time()
        ttft = (self.first_token_time - self.start_time) if self.first_token_time else (self.end_time - self.start_time)
        duration = self.end_time - self.start_time
        
        execution_log.append({
            "model_alias": self.model_alias,
            "model_name": self.actual_model_name,
            "start": self.start_time,
            "end": self.end_time,
            "ttft": ttft,
            "tokens": self.tokens,
            "duration": duration
        })
        print(f"[{self.model_alias}] Finished. Total: {duration:.2f}s, Tokens: {self.tokens}")

# --- 3. Instrument Core LLMs ---
import core.config
import core.llm

# Identify specific models
# Fast = Market, Sustainability
# Tool = Inventory
# Reasoning = Negotiation
handler_fast = DiagnosticHandler("Fast (Market/Sustain)", core.config.MODEL_FAST)
handler_tool = DiagnosticHandler("Tool (Inventory)", core.config.MODEL_TOOL)
handler_reasoning = DiagnosticHandler("Reasoning (Negotiation)", core.config.MODEL_REASONING)

core.llm.llm_fast.callbacks = [handler_fast]
core.llm.llm_tool.callbacks = [handler_tool]
core.llm.llm_reasoning.callbacks = [handler_reasoning]

# --- 4. Patch Market Intelligence ---
from agents.market_intelligence import MarketIntelligenceAgent

def mock_fetch_news(self, query=None):
    return """
    - BREAKING: Massive Cyberattack paralyzes main logistics hub in Singapore.
    - Global shortage of shipping containers reported due to new trade restrictions.
    """

MarketIntelligenceAgent.fetch_news = mock_fetch_news

# --- 5. Run Workflow ---
from workflows.orchestrator_graph import build_graph

def run_workflow():
    print("Building Graph...")
    app = build_graph()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Starting Diagnostic Run (Thread: {thread_id})...")
    
    inputs = {"disruption_signal": "", "risk_assessment": "", "negotiation_plan": "", "audit_result": "", "reasoning_log": []}
    
    try:
        # Run until interrupt (Sustainability Audit)
        for event in app.stream(inputs, config=config):
            pass
    except Exception as e:
        print(f"Error during execution: {e}")

run_workflow()

# Stop monitoring
stop_monitoring.set()
monitor_thread.join(timeout=2)

# --- 6. Generate Report ---
print("\n" + "="*60)
print("             SYSTEM DIAGNOSTIC REPORT")
print("="*60)

# Time to First Token & Model Load Time
print("\n[METRIC 1 & 2] TTFT & Model Load/Switch Time")
print(f"{'Step / Model':<35} | {'TTFT (s)':<10} | {'Status'}")
print("-" * 65)

prev_end_time = 0
prev_model = None

for i, step in enumerate(execution_log):
    model = step['model_name']
    alias = step['model_alias']
    ttft = step['ttft']
    start = step['start']
    
    status = "OK"
    # Heuristic for Cold Start / Switch
    # If TTFT is unusually high (> 2s), implying loading.
    if ttft > 3.0:
        status = "SLOW (Possible Load)"
    
    print(f"{alias:<35} | {ttft:<10.2f} | {status}")
    
    # Check switch time
    if prev_end_time > 0:
        gap = start - prev_end_time
        if prev_model != model:
            print(f"   >>> Switching {prev_model} -> {model}")
            print(f"   >>> Switch Overhead (gap): {gap:.2f}s")
    
    prev_end_time = step['end']
    prev_model = model

# Sequence & Concurrency
print("\n[METRIC 4] Sequence Log")
start_base = execution_log[0]['start'] if execution_log else 0
for step in execution_log:
    rel_start = step['start'] - start_base
    rel_end = step['end'] - start_base
    print(f"[{rel_start:6.2f}s - {rel_end:6.2f}s] {step['model_alias']}")

# Bottlenecks
print("\n[METRIC 5] Bottleneck Identification")
print(f"{'Step':<30} | {'Cause':<20} | {'Confidence'}")
print("-" * 65)

for step in execution_log:
    ttft = step['ttft']
    duration = step['duration']
    gen_time = duration - ttft
    
    # If TTFT dominates duration significantly
    if ttft > 2.0 and ttft > gen_time:
        cause = "Context Loading"
        confidence = "High"
    elif ttft < 1.0 and gen_time > 2.0:
        cause = "Token Generation"
        confidence = "High"
    else:
        cause = "Mixed"
        confidence = "Medium"
        
    print(f"{step['model_alias']:<30} | {cause:<20} | {confidence}")

# VRAM
print("\n[METRIC 3] VRAM/RAM Usage")
if vram_log:
    peaks = [m[1] for m in vram_log]
    avg = sum(peaks)/len(peaks)
    print(f"Peak VRAM: {max(peaks)} MiB")
    print(f"Avg  VRAM: {avg:.0f} MiB")
else:
    print("VRAM data unavailable (nvidia-smi failed or not present).")

if ram_log:
    ram_peaks = [m[1] for m in ram_log]
    print(f"Peak Sys RAM: {max(ram_peaks):.2f} GB")
else:
    print("RAM data unavailable.")

print("="*60)
