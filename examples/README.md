# Blocklog Python SDK Examples

This directory contains example scripts demonstrating Blocklog SDK functionality.

## Quick Start

```bash
pip install blocklog
export BLOCKLOG_API_KEY="blk_..."
python examples/01_quickstart.py
```

## Example Scripts

| File | Description | Lines |
|------|-------------|-------|
| `01_quickstart.py` | Basic quickstart guide | ~100 |
| `02_stock_trading_agent.py` | Stock trading demo | ~400 |
| `03_multi_agent_workflow.py` | Multi-agent orchestration | ~500 |
| `04_team_management.py` | Team and project management | ~150 |
| `05_phase1_features.py` | PHASE 1 new features (NEW!) | ~600 |

## PHASE 1 Features (05_phase1_features.py)

Demonstrates the new PHASE 1 capabilities:

### Agent Identity Management
```python
# Create agent identity
identity = client.agents.create_identity(
    agent_id="payment-agent",
    key_type="ed25519",
)

# Rotate key
client.agents.rotate_key(agent_id="payment-agent")
```

### Delegation Chains
```python
# Create authority delegation
delegation = client.delegations.create(
    issuer_id="user_alice",
    subject_id="payment-agent",
    actions=["transfer", "refund"],
)

# Create delegation chain
client.delegations.create_chain(chain=[
    {"id": "org", "type": "organization"},
    {"id": "user", "type": "user"},
    {"id": "agent", "type": "agent"},
])
```

### Execution Lifecycle
```python
# Create execution
execution = client.executions.create(
    execution_id="exec_123",
    agent_id="agent_abc",
    context={"task": "analyze_data"},
)

# Record steps
client.executions.record_step(
    execution_id="exec_123",
    sequence=1,
    actor_id="agent_abc",
    step_type="MODEL_CALL",
    action="chat_completion",
)

# Update status
client.executions.update_status(
    execution_id="exec_123",
    new_status="COMPLETED",
)
```

### Provenance Graphs
```python
# Create provenance nodes
node = client.provenance.create_node(
    execution_id="exec_123",
    node_type="INPUT",
    content_hash="abc123...",
)

# Create edges
client.provenance.create_edge(
    execution_id="exec_123",
    source_node_id=node.id,
    destination_node_id=step.id,
    relationship_type="INFLUENCED",
)

# Verify freshness
freshness = client.provenance.verify_freshness(
    execution_id="exec_123",
    max_age_minutes=10,
)
```

## Advanced Examples

See the `advanced/` subdirectory for more complex examples:
- LangChain integration
- LangGraph workflows
- Batch processing
- Custom hooks
- Error handling patterns

## Running Examples

```bash
# Set your API key
export BLOCKLOG_API_KEY="your_api_key_here"

# Run an example
python examples/01_quickstart.py

# Or with poetry
poetry run python examples/02_stock_trading_agent.py
```

## Getting Help

- Documentation: `docs/index.md`
- API Reference: `docs/api-reference.md`
- Quickstart: `docs/quickstart.md`
