"""
Example 1: Quickstart
======================
The bare minimum to trace an agent and record a decision with Blocklog.

Run:
    BLOCKLOG_API_KEY=blk_... python 01_quickstart.py
"""

import os

import blocklog

# 1. Initialize the SDK
blocklog.init(api_key=os.environ.get("BLOCKLOG_API_KEY", "blk_demo_key"))


# 2. Record tool calls
@blocklog.tool
def check_price(ticker: str) -> float:
    return 412.50


# 3. Trace your agent
@blocklog.agent(name="simple-trader")
def run_agent():
    price = check_price("TSLA")

    # 4. Record the decision
    with blocklog.decision(type="BUY", asset="TSLA") as d:
        d.record_input(price=price)
        d.record_output(order_id="ord_123")

    print(f"Decision recorded: {d.id}")


if __name__ == "__main__":
    run_agent()
    print("Done. Check your Blocklog dashboard.")
