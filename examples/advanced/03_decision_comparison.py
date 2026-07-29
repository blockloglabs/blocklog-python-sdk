"""
Example 5: Decision Comparison (Forensic Diff)
================================================
Demonstrates how to compare two AI agent runs and identify what changed
between them — useful for debugging model regressions, A/B testing
strategies, and proving that a system change caused a different outcome.

Workflow:
    1. Run baseline agent (e.g. model v1)
    2. Run candidate agent (e.g. model v2)
    3. Use blocklog.replay().compare() to get a forensic diff
    4. Print divergences and decision outcome differences

Run:
    BLOCKLOG_API_KEY=blk_... python 05_decision_comparison.py
    BLOCKLOG_API_KEY=blk_... BASELINE_TRACE=<id> CANDIDATE_TRACE=<id> python 05_decision_comparison.py
"""

import os
import random

import blocklog

blocklog.init(api_key=os.environ.get("BLOCKLOG_API_KEY", "blk_demo_key"))


# ── Define a configurable trading agent ────────────────────────────────────────


def make_agent(model_name: str, bias: float):
    """Factory that creates a named trading agent with a given model bias."""

    @blocklog.tool(name=f"fetch-price-{model_name}")
    def fetch_price(ticker: str) -> float:
        base = {"TSLA": 412.50, "AAPL": 189.30}.get(ticker, 300.0)
        return round(base * (1 + random.uniform(-0.02, 0.02)), 2)

    @blocklog.tool(name=f"compute-signal-{model_name}")
    def compute_signal(price: float, bias: float) -> dict:
        score = round(min(1.0, max(0.0, random.gauss(0.6 + bias, 0.15))), 2)
        return {"signal": "BUY" if score > 0.5 else "HOLD", "score": score}

    @blocklog.agent(
        name=f"trader-{model_name}",
        version=model_name,
        tags=["ab-test", model_name],
    )
    def run(ticker: str = "TSLA") -> dict:
        price = fetch_price(ticker)
        result = compute_signal(price, bias)

        with blocklog.decision(
            type="TRADE_SIGNAL",
            asset=ticker,
            confidence=result["score"],
            metadata={"model": model_name, "bias": bias},
        ) as d:
            d.record_input(price=price, bias=bias)
            d.record_output(signal=result["signal"], score=result["score"])
            d.tag("ab-test", model_name)
            decision_id = d.id

        print(
            f"  [{model_name}] price={price} signal={result['signal']} "
            f"score={result['score']} decision={decision_id}"
        )

        return {
            "decision_id": decision_id,
            "signal": result["signal"],
            "score": result["score"],
            "ticker": ticker,
        }

    return run


def compare_runs(baseline_trace: str, candidate_trace: str) -> None:
    print("\n  Comparing replays:")
    print(f"    Baseline  : {baseline_trace}")
    print(f"    Candidate : {candidate_trace}")
    print()

    try:
        baseline_session = blocklog.replay(baseline_trace)
        print(f"  ✓ Baseline replay session  : {baseline_session.id}")

        comparison = baseline_session.compare(other_trace_id=candidate_trace)
        differences = comparison.get("differences", [])

        print(f"  ✓ Comparison ID            : {comparison.get('id', 'generated')}")
        print(f"  ✓ Differences found        : {len(differences)}")

        if differences:
            print()
            print("  ── Divergences ──────────────────────────────────────────")
            for diff in differences:
                dtype = diff.get("type", "?")
                field = diff.get("field", "?")
                bval = diff.get("baseline_value", "?")
                cval = diff.get("candidate_value", "?")
                desc = diff.get("description", "")
                print(f"    [{dtype}] {field}")
                print(f"      baseline  → {bval}")
                print(f"      candidate → {cval}")
                print(f"      {desc}")
                print()
        else:
            print("  → No divergences detected between the two runs.")

    except Exception as e:
        print(f"  (demo: compare → {e})")
        print()
        print("  ── Simulated Divergences (demo fallback) ────────────────────")
        print("    [decision_outcome] decision")
        print("      baseline  → BUY")
        print("      candidate → HOLD")
        print("      Execution outcome diverged: v1 bought, v2 held.")
        print()
        print("    [summary_counter] event_count")
        print("      baseline  → 8")
        print("      candidate → 6")
        print("      Mismatch in event count — candidate had fewer tool calls.")


if __name__ == "__main__":
    print("=" * 60)
    print("  Blocklog Example 5: Decision Comparison (Forensic Diff)")
    print("=" * 60)
    print()

    # Allow pre-specified trace IDs via env vars (for comparing real runs)
    baseline_trace = os.environ.get("BASELINE_TRACE")
    candidate_trace = os.environ.get("CANDIDATE_TRACE")

    if not baseline_trace or not candidate_trace:
        print("  Running both models to generate fresh traces...")
        print(
            "  (set BASELINE_TRACE and CANDIDATE_TRACE env vars to compare existing traces)"
        )
        print()

        # Model v1 — slight bearish bias
        v1_agent = make_agent("v1-bearish", bias=-0.1)
        v1_result = v1_agent("TSLA")

        # Model v2 — slight bullish bias
        v2_agent = make_agent("v2-bullish", bias=+0.2)
        v2_result = v2_agent("TSLA")

        print()
        print(f"  v1 signal: {v1_result['signal']} (confidence {v1_result['score']})")
        print(f"  v2 signal: {v2_result['signal']} (confidence {v2_result['score']})")

        # Note: for a real comparison we'd use the trace IDs from the
        # agent sessions. In demo mode we use the decision IDs as placeholders.
        baseline_trace = f"trace-from-decision-{v1_result['decision_id']}"
        candidate_trace = f"trace-from-decision-{v2_result['decision_id']}"

    compare_runs(baseline_trace, candidate_trace)

    print("=" * 60)
    print("  ✦ Open your Blocklog dashboard to see:")
    print("    - Side-by-side trace comparison")
    print("    - Divergence list with field-level diffs")
    print("    - Causal graphs for each run")
    print("    - Decision outcome difference (BUY vs HOLD)")
    print("=" * 60)
