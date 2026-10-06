#!/usr/bin/env python3
"""
Blocklog PHASE 1 Examples

Examples demonstrating the new PHASE 1 functionality:
- Agent Identity Management
- Delegation Chains
- Execution Lifecycle
"""

import os

from blocklog import BlocklogClient


def example_agent_identity():
    """
    Create and manage agent cryptographic identities.
    """
    print("=== Agent Identity Example ===\n")

    client = BlocklogClient(api_key=os.environ.get("BLOCKLOG_API_KEY", "test_key"))

    # Create a new identity for an agent
    print("1. Creating agent identity...")
    try:
        identity = client.agents.create_identity(
            agent_id="payment-agent",
            key_type="ed25519",
            metadata={"purpose": "payment-processing"},
            expires_at=None,  # No expiration
        )
        print(f"   Identity created: {identity.key_id}")
        print(f"   Status: {identity.status}")
    except Exception as e:
        print(f"   (Would fail with real API: {e})")

    # List all identities for an agent
    print("\n2. Listing agent identities...")
    try:
        identities = client.agents.list_identities(agent_id="payment-agent")
        print(f"   Found {len(identities)} identities")
    except Exception:
        print("   (Would list identities with real API)")

    # Rotate the agent's key
    print("\n3. Rotating agent key...")
    try:
        new_identity = client.agents.rotate_key(
            agent_id="payment-agent",
            reuse_old=False,  # Revoke old key
        )
        print("   Key rotated successfully")
        print(f"   New key ID: {new_identity.key_id}")
    except Exception:
        print("   (Would rotate key with real API)")


def example_delegation_chain():
    """
    Create and manage authority delegation chains.
    """
    print("\n=== Delegation Chain Example ===\n")

    client = BlocklogClient(api_key=os.environ.get("BLOCKLOG_API_KEY", "test_key"))

    # Create a delegation from user to agent
    print("1. Creating delegation from user to agent...")
    try:
        delegation = client.delegations.create(
            issuer_id="user_alice",
            issuer_type="user",
            subject_id="payment-agent",
            subject_type="agent",
            actions=["transfer", "refund"],
            resources=["funds", "api"],
            policy_id="payment-policy-v1",
            max_depth=10,
            constraints={"rate_limit": 100},
        )
        print(f"   Delegation created: {delegation.id}")
        print(f"   Depth: {delegation.depth}")
    except Exception:
        print("   (Would create delegation with real API)")

    # Create a delegation chain
    print("\n2. Creating delegation chain...")
    try:
        chain = client.delegations.create_chain(
            chain=[
                {"id": "blocklog-org", "type": "organization"},
                {"id": "finance-team", "type": "user"},
                {"id": "payment-agent", "type": "agent"},
                {"id": "sub-agent-1", "type": "agent"},
            ],
            policy_id="payment-policy-v1",
        )
        print(f"   Chain created with {len(chain.delegations)} links")
    except Exception:
        print("   (Would create chain with real API)")

    # Resolve authority for an agent
    print("\n3. Resolving authority for payment-agent...")
    try:
        authority = client.delegations.resolve_authority(
            subject_id="payment-agent",
            subject_type="agent",
            action="transfer",
            resource="funds",
        )
        print(f"   Is authorized: {authority.is_authorized}")
        print(f"   Policy: {authority.policy}")
        print(f"   Chain depth: {len(authority.chain)}")
    except Exception:
        print("   (Would resolve authority with real API)")


def example_execution_lifecycle():
    """
    Manage agent execution lifecycles.
    """
    print("\n=== Execution Lifecycle Example ===\n")

    client = BlocklogClient(api_key=os.environ.get("BLOCKLOG_API_KEY", "test_key"))

    # Create a new execution
    print("1. Creating execution...")
    try:
        execution = client.executions.create(
            execution_id="exec_12345",
            agent_id="payment-agent",
            agent_version="1.0.0",
            principal_id="user_alice",
            principal_type="user",
            policy_id="payment-policy-v1",
            policy_version=1,
            context={
                "action": "transfer",
                "amount": 50000,
                "destination": "account_12345",
            },
            context_provenance={"source": "user_request"},
        )
        print(f"   Execution started: {execution.execution_id}")
        print(f"   Status: {execution.status}")
    except Exception:
        print("   (Would create execution with real API)")

    # Record execution steps
    print("\n2. Recording execution steps...")
    try:
        step1 = client.executions.record_step(
            execution_id="exec_12345",
            sequence=1,
            actor_id="payment-agent",
            actor_type="agent",
            step_type="MODEL_CALL",
            action="chat_completion",
            input_hash="abc123def456...",
            output_hash="xyz789ghi012...",
            status="SUCCESS",
        )
        print(f"   Step 1 recorded: {step1.step_type}")

        step2 = client.executions.record_step(
            execution_id="exec_12345",
            sequence=2,
            actor_id="payment-agent",
            actor_type="agent",
            step_type="TOOL_CALL",
            action="transfer_funds",
            input_hash="xyz789...",
            output_hash="ghi012...",
            status="SUCCESS",
        )
        print(f"   Step 2 recorded: {step2.step_type}")
    except Exception:
        print("   (Would record steps with real API)")

    # Update execution status
    print("\n3. Updating execution status...")
    try:
        execution = client.executions.update_status(
            execution_id="exec_12345",
            new_status="COMPLETED",
        )
        print(f"   Status updated to: {execution.status}")
    except Exception:
        print("   (Would update status with real API)")

    # List executions
    print("\n4. Listing executions...")
    try:
        executions = client.executions.list(
            agent_id="payment-agent",
            status="COMPLETED",
        )
        print(f"   Found {len(executions)} completed executions")
    except Exception:
        print("   (Would list executions with real API)")


def example_provenance():
    """
    Create and verify provenance graphs.
    """
    print("\n=== Provenance Graph Example ===\n")

    client = BlocklogClient(api_key=os.environ.get("BLOCKLOG_API_KEY", "test_key"))

    # Create provenance nodes
    print("1. Creating provenance nodes...")
    try:
        # Input node
        input_node = client.provenance.create_node(
            execution_id="exec_12345",
            node_type="INPUT",
            content_hash="abc123...",
            source="human",
            source_metadata={"user": "alice", "source": "prompt"},
            freshness_minutes=5,
            trust_level="HIGH",
        )
        print(f"   Input node created: {input_node.node_type}")

        # Decision node
        decision_node = client.provenance.create_node(
            execution_id="exec_12345",
            node_type="DECISION",
            content_hash="def456...",
            source="model",
            trust_level="HIGH",
        )
        print(f"   Decision node created: {decision_node.node_type}")
    except Exception:
        print("   (Would create nodes with real API)")

    # Create provenance edges
    print("\n2. Creating provenance edges...")
    try:
        edge = client.provenance.create_edge(
            execution_id="exec_12345",
            source_node_id=input_node.id,
            destination_node_id=decision_node.id,
            relationship_type="INFLUENCED",
            metadata={"direction": "forward"},
        )
        print(f"   Edge created: {edge.relationship_type}")
    except Exception:
        print("   (Would create edge with real API)")

    # Get provenance graph
    print("\n3. Getting provenance graph...")
    try:
        graph = client.provenance.get_execution_graph(execution_id="exec_12345")
        print(f"   Nodes: {graph.node_count}")
        print(f"   Edges: {graph.edge_count}")
    except Exception:
        print("   (Would get graph with real API)")

    # Verify freshness
    print("\n4. Verifying input freshness...")
    try:
        freshness = client.provenance.verify_freshness(
            execution_id="exec_12345",
            max_age_minutes=10,
        )
        print(f"   Is fresh: {freshness.is_fresh}")
        print(f"   Fresh inputs: {freshness.fresh_count}")
        print(f"   Stale inputs: {freshness.stale_count}")
    except Exception:
        print("   (Would verify freshness with real API)")


def example_end_to_end():
    """
    Complete end-to-end example: Agent execution with all features.
    """
    print("\n=== End-to-End Example ===\n")

    client = BlocklogClient(api_key=os.environ.get("BLOCKLOG_API_KEY", "test_key"))

    # 1. Create agent identity
    print("1. Creating agent identity...")
    client.agents.create_identity(agent_id="payment-agent")

    # 2. Set up delegation chain
    print("2. Setting up delegation...")
    client.delegations.create(
        issuer_id="finance-team",
        issuer_type="user",
        subject_id="payment-agent",
        subject_type="agent",
        actions=["transfer", "refund"],
        resources=["funds"],
        policy_id="payment-policy-v1",
    )

    # 3. Create execution
    print("3. Creating execution...")
    client.executions.create(
        execution_id="exec_e2e_001",
        agent_id="payment-agent",
        policy_id="payment-policy-v1",
        context={"action": "transfer", "amount": 50000},
    )

    # 4. Record steps
    print("4. Recording steps...")
    step1 = client.executions.record_step(
        execution_id="exec_e2e_001",
        sequence=1,
        actor_id="payment-agent",
        step_type="MODEL_CALL",
        action="chat_completion",
    )

    client.executions.record_step(
        execution_id="exec_e2e_001",
        sequence=2,
        actor_id="payment-agent",
        step_type="TOOL_CALL",
        action="transfer_funds",
        status="SUCCESS",
    )

    # 5. Create provenance
    print("5. Creating provenance edges...")
    input_node = client.provenance.create_node(
        execution_id="exec_e2e_001",
        node_type="INPUT",
        content_hash="abc123...",
    )

    client.provenance.create_edge(
        execution_id="exec_e2e_001",
        source_node_id=input_node.id,
        destination_node_id=step1.id,
        relationship_type="INFLUENCED",
    )

    # 6. Complete execution
    print("6. Completing execution...")
    client.executions.update_status(
        execution_id="exec_e2e_001",
        new_status="COMPLETED",
    )

    print("\n   ✅ End-to-end execution complete!")


if __name__ == "__main__":
    print("Blocklog PHASE 1 Examples")
    print("=" * 50)

    # Note: These examples require valid API keys
    api_key = os.environ.get("BLOCKLOG_API_KEY")
    if not api_key:
        print("\n⚠️  Set BLOCKLOG_API_KEY environment variable to run examples\n")

    example_agent_identity()
    example_delegation_chain()
    example_execution_lifecycle()
    example_provenance()
    example_end_to_end()

    print("\n" + "=" * 50)
    print("Examples complete!")
