# System Diagnostic Report (Optimized)
**Date:** 2026-02-06
**Subject:** Autonomous Supply Chain Orchestrator Performance Analysis (Post-Optimization)

## Executive Summary
The system model configuration was optimized to use `llama3.2` (for Fast/Tool) and `deepseek-r1:1.5b` (for Reasoning). 
**Result:** The orchestration workflow now runs to completion with no stalls. VRAM usage is well within limits (Max 74%). The bottleneck between Step 1 and 2 was eliminated.

## 1. Performance Metrics (Optimized)

| Step | Model (Alias) | TTFT (s) | Load/Switch Time (s) | Duration (s) | Status |
|------|---------------|----------|----------------------|--------------|--------|
| **1** | Llama 3.2 (Fast) | 7.32s | - | 12.18s | OK |
| **2** | Llama 3.2 (Tool) | **3.17s** | **0.0s** | 29.92s | **FAST (Cached)** |
| **3** | DeepSeek 1.5b | 28.74s | ~10.0s | 72.00s | **SUCCESS** |
| **4** | Llama 3.2 (Fast) | 26.67s | ~10.0s | 59.35s | OK |

**Improvements:**
- **Step 2 Latency:** Reduced from ~13s to 3s (eliminated 10s switch delay).
- **Step 3 Reliability:** Reasoning step now completes successfully (previously stalled).
- **Throughput:** Reasoning model generates ~13 tokens/s (949 tokens in 72s).

## 2. Resource Usage (Peak)

| Metric | Measured Value | Limit | Utilization | Status |
|--------|----------------|-------|-------------|--------|
| **VRAM** | **1512 MiB** | 2048 MiB | **74%** | **HEALTHY** |
| **RAM** | 12.43 GB | - | - | OK |
| **GPU** | GeForce MX450 | - | 43-100% | OK |

**Analysis:**
VRAM usage dropped from critically high (>90% implied share) to a comfortable 74%. The system is no longer thrashing swap memory, allowing `deepseek-r1:1.5b` to run efficiently.

## 3. Sequence Log
Models ran sequentially with expected switch overheads only for Step 3 and 4.

`[000s - 012s]` Fast (Market)
`[012s - 048s]` Tool (Inventory) - *Seamless transition*
`[049s - 121s]` Reasoning (Negotiation) - *Switch to 1.5b*
`[121s - 180s]` Fast (Audit) - *Switch back to Llama*

## 4. Final Recommendation
The current configuration (`llama3.2` + `deepseek-r1:1.5b`) is **stable and efficient** for the local MX450 hardware. 

**Future Optimizations:**
- **Keep Warming:** If possible, keep both models loaded in RAM (requires ~3-4GB system RAM) to reduce the 25s switch time for Step 3/4, using `ollama run <model> --keepalive -1`.
