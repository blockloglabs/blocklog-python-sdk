"""
Executions API Module

Provides high-level interface for managing agent executions with full lifecycle tracking.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from blocklog.models.execution import Execution, ExecutionStep, ExecutionApproval


class ExecutionsAPI:
    """Client for execution management API."""
    
    def __init__(self, client):
        self._client = client
    
    def create(
        self,
        execution_id: str,
        agent_id: Optional[str] = None,
        agent_version: Optional[str] = None,
        principal_id: Optional[str] = None,
        principal_type: Optional[str] = None,
        authority_chain: Optional[Dict[str, Any]] = None,
        policy_id: Optional[str] = None,
        policy_version: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        context_provenance: Optional[Dict[str, Any]] = None,
        timeout_at: Optional[datetime] = None,
    ) -> Execution:
        """
        Create a new execution record.
        
        Args:
            execution_id: External facing execution ID
            agent_id: Agent performing the execution
            agent_version: Version of the agent
            principal_id: User or agent that initiated the execution
            principal_type: Type of principal ('user', 'agent')
            authority_chain: Delegation chain information
            policy_id: Policy governing this execution
            policy_version: Policy version at time of execution
            context: Execution context (input data)
            context_provenance: Where context came from
            timeout_at: Optional timeout for execution
            
        Returns:
            Execution: Created execution record
        """
        # The backend declares these as FastAPI query parameters, not a JSON body.
        response = self._client._post(
            "/executions/",
            params={
                "execution_id": execution_id,
                "agent_id": agent_id,
                "agent_version": agent_version,
                "principal_id": principal_id,
                "principal_type": principal_type,
                "authority_chain": authority_chain,
                "policy_id": policy_id,
                "policy_version": policy_version,
                "context": context,
                "context_provenance": context_provenance,
                "timeout_at": timeout_at.isoformat() if timeout_at else None,
            },
        )
        return Execution(**response)
    
    def get(self, execution_id: str) -> Execution:
        """
        Get execution by external ID.
        
        Args:
            execution_id: External facing execution ID
            
        Returns:
            Execution: Execution record
        """
        response = self._client._get(f"/executions/{execution_id}")
        return Execution(**response)
    
    def list(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Execution]:
        """
        List executions with optional filters.
        
        Args:
            agent_id: Optional agent filter
            status: Optional status filter
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of Execution records
        """
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
            
        response = self._client._get("/executions", params=params)
        return [Execution(**e) for e in response.get("executions", [])]
    
    def update_status(
        self,
        execution_id: str,
        new_status: str,
        completed_at: Optional[datetime] = None,
    ) -> Execution:
        """
        Update execution status.
        
        Args:
            execution_id: External facing execution ID
            new_status: Target status
            completed_at: Optional completion timestamp
            
        Returns:
            Execution: Updated execution record
        """
        json_data = {"new_status": new_status}
        if completed_at:
            json_data["completed_at"] = completed_at.isoformat()
            
        response = self._client._post(
            f"/executions/{execution_id}/status",
            params=json_data,
        )
        return Execution(**response)
    
    def record_step(
        self,
        execution_id: str,
        sequence: int,
        actor_id: str,
        actor_type: str = "agent",
        step_type: str = None,
        action: str = None,
        input_hash: Optional[str] = None,
        input_metadata: Optional[Dict[str, Any]] = None,
        output_hash: Optional[str] = None,
        output_metadata: Optional[Dict[str, Any]] = None,
        status: str = "PENDING",
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        evidence_path: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None,
    ) -> ExecutionStep:
        """
        Record an execution step.
        
        Args:
            execution_id: External facing execution ID
            sequence: Step sequence number
            actor_id: Agent or user ID that performed the step
            actor_type: Type of actor ('agent', 'user')
            step_type: Type of step
            action: Action performed
            input_hash: SHA-256 hash of input
            input_metadata: Structured input metadata
            output_hash: SHA-256 hash of output
            output_metadata: Structured output metadata
            status: Step status
            error_message: Error message if failed
            error_code: Error code if failed
            evidence_path: Causal relationships
            signature: Optional signature
            
        Returns:
            ExecutionStep: Created step record
        """
        json_data = {
            "sequence": sequence,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "step_type": step_type,
            "action": action,
            "input_hash": input_hash,
            "input_metadata": input_metadata,
            "output_hash": output_hash,
            "output_metadata": output_metadata,
            "status": status,
            "error_message": error_message,
            "error_code": error_code,
            "evidence_path": evidence_path,
            "signature": signature,
        }
        
        response = self._client._post(
            f"/executions/{execution_id}/steps",
            params=json_data,
        )
        return ExecutionStep(**response)
    
    def get_steps(self, execution_id: str) -> List[ExecutionStep]:
        """
        Get all steps for an execution.
        
        Args:
            execution_id: External facing execution ID
            
        Returns:
            List of ExecutionStep records
        """
        response = self._client._get(f"/executions/{execution_id}/steps")
        return [ExecutionStep(**s) for s in response.get("steps", [])]
