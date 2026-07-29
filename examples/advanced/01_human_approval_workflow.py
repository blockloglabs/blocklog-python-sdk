"""
Example 3: Human Approval Workflow
=====================================
Demonstrates how to gate AI decisions on human approval:

    1. Agent proposes a large trade
    2. blocklog.decision() records the decision
    3. d.request_approval() notifies the reviewer (non-blocking)
    4. Reviewer approves or rejects via blocklog.approval.*
    5. Full audit trail is fetched and printed

Run:
    BLOCKLOG_API_KEY=blk_... python 03_human_approval_workflow.py
"""

import os
import random
import time

import blocklog

blocklog.init(api_key=os.environ.get("BLOCKLOG_API_KEY", "blk_demo_key"))

APPROVAL_THRESHOLD = 5_000  # trades above this need human sign-off


@blocklog.tool(name="fetch-price")
def fetch_price(ticker: str) -> float:
    return {"TSLA": 412.50, "NVDA": 875.10, "AAPL": 189.30}.get(ticker, 300.0)


@blocklog.agent(name="large-trade-agent", version="1.0", tags=["high-value"])
def propose_trade(ticker: str, qty: int) -> dict:
    price = fetch_price(ticker)
    value = price * qty

    print(f"  Proposing {qty}x {ticker} @ ${price:.2f} = ${value:,.2f}")

    with blocklog.decision(
        type="LARGE_TRADE",
        asset=ticker,
        confidence=0.91,
        metadata={"strategy": "momentum", "portfolio": "equity-long"},
    ) as d:
        d.record_input(price=price, qty=qty, trade_value=value)
        d.tag("large-value")

        if value > APPROVAL_THRESHOLD:
            print(
                f"\n  ⚠️  Trade value ${value:,.2f} exceeds ${APPROVAL_THRESHOLD:,} threshold"
            )
            print("  → Requesting human approval (non-blocking)...")

            # This fires the approval request and returns immediately.
            # The reviewer will be notified via webhook/email.
            d.request_approval(
                reason=f"Trade value ${value:,.2f} exceeds the ${APPROVAL_THRESHOLD:,} auto-execution limit.",
                reviewer="risk-officer@fund.com",
            )

        d.record_output(
            status="pending_approval" if value > APPROVAL_THRESHOLD else "auto_approved"
        )
        decision_id = d.id

    return {"decision_id": decision_id, "ticker": ticker, "qty": qty, "value": value}


def simulate_approval_workflow(decision_id: str) -> None:
    """Simulate a reviewer approving/rejecting the decision."""
    print("\n── Simulating Review Process ──────────────────────────────────")

    # In a real system, the reviewer would receive a notification and
    # take action in the Blocklog dashboard or via their own tooling.
    # Here we simulate the reviewer using the SDK directly.

    print("  [Reviewer] Examining decision...")
    time.sleep(0.5)

    action = random.choice(["approve", "reject", "escalate"])

    if action == "approve":
        print("  [Reviewer] Approving decision...")
        try:
            blocklog.approval.request(
                decision_id=decision_id,
                reason="Trade reviewed and approved by risk officer.",
                reviewer="risk-officer@fund.com",
            )
            print("  ✓ Approval recorded")
        except Exception as e:
            print(f"  (demo mode: {e})")

    elif action == "reject":
        print("  [Reviewer] Rejecting decision...")
        try:
            blocklog.approval.reject(
                reviewer="risk-officer@fund.com",
                reason="Insufficient market liquidity for trade size.",
                decision_id=decision_id,
            )
            print("  ✗ Rejection recorded")
        except Exception as e:
            print(f"  (demo mode: {e})")

    elif action == "escalate":
        print("  [Reviewer] Escalating to head of risk...")
        try:
            blocklog.approval.escalate(
                from_reviewer="risk-officer@fund.com",
                to_reviewer="cro@fund.com",
                reason="Trade size requires CRO sign-off per policy.",
            )
            print("  ↑ Escalation recorded")
        except Exception as e:
            print(f"  (demo mode: {e})")

    # Fetch the audit trail
    print("\n── Approval Audit Trail ────────────────────────────────────────")
    try:
        trail = blocklog.approval.audit_trail()
        if trail:
            for entry in trail[:3]:
                print(
                    f"  [{entry.get('action', '?').upper()}]"
                    f"  reviewer={entry.get('reviewer', '?')}"
                    f"  ts={entry.get('timestamp', '?')}"
                )
        else:
            print("  (no audit events yet — check dashboard)")
    except Exception as e:
        print(f"  (demo mode: {e})")


if __name__ == "__main__":
    print("=" * 60)
    print("  Blocklog Example 3: Human Approval Workflow")
    print("=" * 60)
    print()

    # Run the agent — it will request approval for large trades
    result = propose_trade("NVDA", qty=30)

    print(f"\n  Decision ID : {result['decision_id']}")
    print(f"  Trade value : ${result['value']:,.2f}")
    print(f"  Threshold   : ${APPROVAL_THRESHOLD:,}")

    if result["value"] > APPROVAL_THRESHOLD:
        simulate_approval_workflow(result["decision_id"])
    else:
        print("\n  Trade was below threshold — auto-approved, no review needed.")

    print()
    print("=" * 60)
    print("  ✦ Open your Blocklog dashboard to see:")
    print("    - The LARGE_TRADE decision with approval request")
    print("    - The HITL audit trail (approve/reject/escalate)")
    print("    - Reviewer identity and timestamp")
    print("=" * 60)
