# Sagepilot AI TAM Coding Assignment (Part B2)
**Submitted by:** Karthik Raveendran  
**Date:** July 14, 2026

Here is my implementation of the stateful Order Supervisor simulation. The engine is written in pure Python without external dependencies (unless running with the optional live LLM mode) to make it easy to run and review during our call.

---

## How to Run the Simulator

### 1. Requirements
*   **Python 3.8+** (runs completely out of the box).
*   *Optional (Bonus):* If you want to run it using a live OpenAI or Gemini API model instead of the default rule-based simulator:
    ```bash
    pip install openai google-generativeai
    
    # Set the key in your terminal session
    $env:OPENAI_API_KEY="your-key-here"  # Windows PowerShell
    # or
    $env:GEMINI_API_KEY="your-key-here"
    ```

### 2. Run Commands
Run the default order event simulation (`events.json`):
```bash
python simulator.py
```

Run my scenario test suite containing both happy and unhappy path test cases:
```bash
python test_scenarios.py
```

---

## Production Mapping: Temporal Primitives

Here is how each code block I built maps to actual production concepts in a Temporal-based system:

1.  **Incoming Order Events** (e.g., `payment_confirmed`, `customer_message_received`) ➔ **Signals**
    *   *Production Mapping:* Webhooks from Shopify or Meta are caught by our gateway and dispatched to the specific running order workflow as asynchronous signals to update state variables without polling.
2.  **Virtual 24-Hour Timer Loop** ➔ **Timer (Durable Sleep)**
    *   *Production Mapping:* Workflows call `workflow.Sleep(24 * time.Hour)` when waiting for shipping updates. Temporal stores this in its database, shutting down active worker compute. Once the timer fires, the workflow worker wakes up and picks up execution right where it left off.
3.  **Rolling Memory Summary & Timeline Reads** ➔ **Queries**
    *   *Production Mapping:* External admin dashboards or frontends read the current compacted memory status by calling a Temporal Query on the running workflow instance, returning the state instantly without changing it.
4.  **Mock Activities** (`message_customer`, `escalate`, etc.) ➔ **Activities**
    *   *Production Mapping:* Non-deterministic API calls, emails, and database writes are wrapped inside Temporal Activities. This guarantees that if the API fails, the framework automatically retries with exponential backoffs, keeping the core workflow deterministic.
5.  **State Compaction** ➔ **Continue-As-New**
    *   *Production Mapping:* A supervisor tracking an order for weeks accumulates a huge history of logs in Temporal. To avoid hitting size limits and degrading worker performance, the workflow calls `ContinueAsNew`, restarting itself with a clean history and passing the compacted memory block forward.

---

## How an LLM Improves the Decision Logic

In my code, `agent_reasoning()` handles what happens when the supervisor wakes up. I structured it so you can pass in a unified prompt containing:
1.  The order metadata (customer details, order ID, status).
2.  The compacted history summary (rolling memory).
3.  The chronological list of recent events (active timeline).
4.  The triggering event and payload (e.g., the raw customer WhatsApp message).

### Why this beats simple hardcoded rules:
*   **Semantic Intent Mapping**: A rule-based parser searches for keywords like "refund", which misses context. An LLM reads the customer's text (e.g., *"the box got destroyed in transit, and it leaked everywhere"*) and correctly classifies it as a damage complaint rather than a standard return query.
*   **Sentiment Escalations**: The LLM flags high-risk statements (e.g., *"I'm filing a chargeback"*) and triggers the `escalate()` activity immediately.
*   **Dynamic and Personal Copy**: Instead of dry templates, the LLM constructs an empathetic response explaining *why* the carrier is delayed (e.g., apologizing for Delhivery issues due to regional monsoons) which helps keep CSAT high.
