"""
Example 4: Incident Investigation
=====================================
Demonstrates the full incident investigation workflow:

    1. An anomaly is detected in a trade decision
    2. An incident is created and assigned
    3. A forensic replay session is spun up on the trace
    4. Root cause analysis is run
    5. Findings are annotated on the incident
    6. The incident is resolved and closed

Run:
    BLOCKLOG_API_KEY=blk_... python 04_incident_investigation.py
"""

import os

import blocklog

blocklog.init(api_key=os.environ.get("BLOCKLOG_API_KEY", "blk_demo_key"))

# Simulated trace ID from a previous agent run that produced an anomaly
ANOMALOUS_TRACE_ID = os.environ.get("ANOMALOUS_TRACE_ID", "trace-demo-12345")


def investigate(trace_id: str) -> None:
    print(f"  Investigating trace: {trace_id}\n")

    # ── Step 1: Create the incident ──────────────────────────────────────────
    print("  [1/5] Creating incident...")
    try:
        inc = blocklog.incident.create(
            title="Unexpected SELL on AAPL — anomalous decision detected",
            trace_id=trace_id,
            severity="high",
            description=(
                "Automated anomaly detection flagged a SELL decision on AAPL "
                "that contradicts the current momentum strategy. "
                "Investigating whether stale context or policy violation caused this."
            ),
        )
        print(f"        ✓ Incident created: {inc.id}")
    except Exception as e:
        print(f"        (demo: incident.create() → {e})")

        # Create a mock handle for demo purposes
        class _MockIncident:
            id = "inc_demo_001"
            status = "open"

            def assign(self, *a, **kw):
                return self

            def annotate(self, *a, **kw):
                return {}

            def resolve(self, *a, **kw):
                return self

            def close(self, *a, **kw):
                return self

            def report(self):
                return {"status": "generated"}

        inc = _MockIncident()

    # ── Step 2: Assign the incident ───────────────────────────────────────────
    print("\n  [2/5] Assigning to investigation team...")
    try:
        inc.assign(
            assignee="alice@fund.com",
            notes="Alice is the senior quant on AAPL desk — best placed to investigate.",
        )
        print("        ✓ Assigned to alice@fund.com")
    except Exception as e:
        print(f"        (demo: assign → {e})")

    # ── Step 3: Forensic replay ───────────────────────────────────────────────
    print("\n  [3/5] Creating forensic replay session...")
    root_cause_description = "No anomaly detected — system operating normally."
    root_cause_remediation = "N/A"

    try:
        session = blocklog.replay(trace_id)
        print(f"        ✓ Replay session: {session.id}")

        # Get the timeline
        timeline = session.timeline()
        print(f"        → Timeline events: {len(timeline)}")

        # Run root cause analysis
        print("\n  [4/5] Running root cause analysis...")
        cause = session.root_cause()
        print(f"        detected       : {cause.get('detected', False)}")
        print(f"        root_cause_type: {cause.get('root_cause_type', 'UNKNOWN')}")
        print(f"        description    : {cause.get('description', 'N/A')}")
        print(f"        confidence     : {cause.get('confidence', 0.0):.0%}")
        print(f"        remediation    : {cause.get('remediation', 'N/A')}")

        root_cause_description = cause.get("description", root_cause_description)
        root_cause_remediation = cause.get("remediation", root_cause_remediation)

        # Check staleness
        stale = session.staleness()
        rating = stale.get("overall_staleness_rating", "unknown")
        findings = stale.get("findings", [])
        print(f"\n        Staleness rating : {rating}")
        for f in findings[:2]:
            print(
                f"          - {f.get('path', '?')} | stale={f.get('stale')} | risk={f.get('risk_score')}"
            )

    except Exception as e:
        print(f"        (demo: replay → {e})")
        print("\n  [4/5] Root cause analysis (demo fallback)...")
        print(
            "        Root cause: STALE_CONTEXT — data source was 47s stale (limit: 30s)"
        )
        root_cause_description = (
            "Execution relied on stale price feed data (age 47s, limit 30s)."
        )
        root_cause_remediation = (
            "Reduce data cache TTL to 20s or add freshness gate before execution."
        )

    # ── Step 5: Annotate and resolve ──────────────────────────────────────────
    print("\n  [5/5] Annotating and resolving incident...")
    try:
        inc.annotate(
            f"Root cause: {root_cause_description}",
            author="alice@fund.com",
        )
        inc.annotate(
            f"Remediation: {root_cause_remediation}",
            author="alice@fund.com",
        )
        print("        ✓ Annotations added")

        inc.resolve(
            summary=root_cause_description,
            root_cause="STALE_CONTEXT",
            remediation_actions=[root_cause_remediation],
        )
        print("        ✓ Incident resolved")

        inc.close(
            notes="Root cause confirmed and remediation deployed.",
            approval_status="approved",
        )
        print("        ✓ Incident closed")

        report = inc.report()
        print(f"        ✓ Investigation report: {report.get('id', 'generated')}")

    except Exception as e:
        print(f"        (demo: resolve/close → {e})")


if __name__ == "__main__":
    print("=" * 60)
    print("  Blocklog Example 4: Incident Investigation")
    print("=" * 60)
    print()
    print(f"  Trace ID: {ANOMALOUS_TRACE_ID}")
    print("  (set ANOMALOUS_TRACE_ID env var to investigate a real trace)")
    print()

    investigate(ANOMALOUS_TRACE_ID)

    print()
    print("=" * 60)
    print("  ✦ Open your Blocklog dashboard to see:")
    print("    - The incident with full lifecycle history")
    print("    - The replay session with timeline + causal graph")
    print("    - Root cause analysis with confidence score")
    print("    - Staleness heatmap for data sources")
    print("    - Investigation report")
    print("=" * 60)
