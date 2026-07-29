"""
Example 2: Multi-Agent Hedge Fund
===================================
Demonstrates how multiple Blocklog-instrumented agents collaborate:

    - AnalystAgent  — analyses market conditions, produces a BUY/SELL signal
    - RiskAgent     — validates the signal against risk limits
    - ExecutorAgent — executes the trade if risk is approved

Each agent produces its own trace, decisions, and tool calls.
A final compliance report is generated over the full workflow.

Run:
    BLOCKLOG_API_KEY=blk_... python 02_multi_agent_hedge_fund.py
"""

import os
import random
from uuid import uuid4

import blocklog

blocklog.init(api_key=os.environ.get("BLOCKLOG_API_KEY", "blk_demo_key"))

# Shared workflow ID so all agents are linked
WORKFLOW_ID = str(uuid4())
print(f"✦ Workflow ID: {WORKFLOW_ID}\n")


# ── Tools (shared across agents) ──────────────────────────────────────────────


@blocklog.tool(name="fetch-price")
def fetch_price(ticker: str) -> float:
    return {"TSLA": 412.50, "AAPL": 189.30, "NVDA": 875.10}.get(ticker, 250.0)


@blocklog.tool(name="compute-momentum-score")
def momentum_score(price: float, volume: int) -> float:
    return round(min(1.0, (volume / 3_000_000) * (price / 500)), 2)


@blocklog.tool(name="check-risk-limits")
def check_risk_limits(ticker: str, qty: int, price: float) -> dict:
    trade_value = qty * price
    return {
        "approved": trade_value < 50_000,
        "trade_value": trade_value,
        "limit": 50_000,
        "utilisation": round(trade_value / 50_000, 2),
    }


@blocklog.tool(name="execute-trade")
def execute_trade(ticker: str, qty: int, price: float) -> dict:
    return {
        "order_id": f"ord_{random.randint(10000, 99999)}",
        "filled_at": price * 1.0008,
        "qty": qty,
        "total_value": qty * price,
    }


# ── Agent 1: Market Analyst ────────────────────────────────────────────────────


@blocklog.agent(name="market-analyst", version="2.1", tags=["analysis"])
def analyst_agent(ticker: str) -> dict:
    print(f"[Analyst] Analysing {ticker}...")

    price = fetch_price(ticker)
    volume = random.randint(1_000_000, 4_000_000)
    score = momentum_score(price, volume)

    signal = "BUY" if score > 0.5 else "HOLD"

    with blocklog.decision(
        type="SIGNAL",
        asset=ticker,
        confidence=score,
        metadata={"workflow_id": WORKFLOW_ID, "agent": "market-analyst"},
    ) as d:
        d.record_input(price=price, volume=volume)
        d.record_output(signal=signal, momentum_score=score)
        d.tag("analysis", "momentum")
        signal_decision_id = d.id

    print(
        f"[Analyst] Signal: {signal} (score={score}) — decision: {signal_decision_id}"
    )
    return {
        "ticker": ticker,
        "price": price,
        "signal": signal,
        "confidence": score,
        "decision_id": signal_decision_id,
    }


# ── Agent 2: Risk Manager ──────────────────────────────────────────────────────


@blocklog.agent(name="risk-manager", version="1.5", tags=["risk"])
def risk_agent(ticker: str, price: float, qty: int, analyst_decision_id: str) -> dict:
    print(f"[Risk] Checking limits for {qty}x {ticker}...")

    risk = check_risk_limits(ticker, qty, price)

    with blocklog.decision(
        type="RISK_APPROVAL",
        asset=ticker,
        confidence=1.0 if risk["approved"] else 0.0,
        metadata={"workflow_id": WORKFLOW_ID, "agent": "risk-manager"},
    ) as d:
        d.record_input(
            qty=qty,
            price=price,
            trade_value=risk["trade_value"],
            limit=risk["limit"],
            analyst_decision_id=analyst_decision_id,
        )
        d.record_output(
            approved=risk["approved"],
            utilisation=risk["utilisation"],
        )
        d.tag("risk-check")

        if not risk["approved"]:
            d.request_approval(
                reason=f"Trade ${risk['trade_value']:.0f} exceeds limit ${risk['limit']:.0f}",
                reviewer="cro@fund.com",
            )

        risk_decision_id = d.id

    status = "✓ APPROVED" if risk["approved"] else "✗ REJECTED (approval requested)"
    print(f"[Risk] {status} — decision: {risk_decision_id}")
    return {**risk, "risk_decision_id": risk_decision_id}


# ── Agent 3: Execution Engine ──────────────────────────────────────────────────


@blocklog.agent(name="executor", version="1.0", tags=["execution"])
def executor_agent(ticker: str, qty: int, price: float, risk_decision_id: str) -> dict:
    print(f"[Executor] Executing {qty}x {ticker}...")

    order = execute_trade(ticker, qty, price)

    with blocklog.decision(
        type="TRADE_EXECUTION",
        asset=ticker,
        confidence=0.99,
        metadata={"workflow_id": WORKFLOW_ID, "agent": "executor"},
    ) as d:
        d.record_input(
            qty=qty,
            price=price,
            risk_decision_id=risk_decision_id,
        )
        d.record_output(
            order_id=order["order_id"],
            filled_at=order["filled_at"],
            total_value=order["total_value"],
        )
        d.tag("execution", "filled")
        execution_decision_id = d.id

    print(
        f"[Executor] Filled: order {order['order_id']} — decision: {execution_decision_id}"
    )
    return {**order, "execution_decision_id": execution_decision_id}


# ── Orchestrator ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TICKER = "TSLA"
    QTY = 50

    print("=" * 60)
    print("  Blocklog Example 2: Multi-Agent Hedge Fund")
    print("=" * 60)
    print()

    # Step 1: Market analysis
    analysis = analyst_agent(TICKER)

    if analysis["signal"] != "BUY":
        print("\n[Orchestrator] No BUY signal from analyst — stopping workflow.")
    else:
        # Step 2: Risk check
        price = analysis["price"]
        risk = risk_agent(TICKER, price, QTY, analysis["decision_id"])

        if risk["approved"]:
            # Step 3: Execution
            result = executor_agent(TICKER, QTY, price, risk["risk_decision_id"])

            # Step 4: Generate compliance report for the workflow
            print("\n[Orchestrator] Generating compliance report...")
            try:
                report = blocklog.compliance.generate(
                    metadata={"workflow_id": WORKFLOW_ID, "tickers": [TICKER]},
                    framework="SOC2",
                )
                print(
                    f"[Orchestrator] Compliance report: {report.get('id', 'generated')}"
                )
            except Exception as e:
                print(f"[Orchestrator] (compliance skipped in demo: {e})")
        else:
            print("\n[Orchestrator] Risk rejected — awaiting human approval.")

    print()
    print("=" * 60)
    print("  ✦ Open your Blocklog dashboard to see:")
    print("    - Three separate agent traces linked by workflow_id")
    print("    - Signal → Risk → Execution decision chain")
    print("    - HITL approval request (if risk was exceeded)")
    print("    - Compliance report for the full workflow")
    print("=" * 60)
