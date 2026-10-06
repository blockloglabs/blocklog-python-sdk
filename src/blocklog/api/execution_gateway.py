"""
blocklog.api.execution_gateway
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Layer 2 client for execution gateway features (PHASE 2 & 3):

- Risk assessment calculation and storage
- Policy evaluation with risk scoring
- Token consumption tracking (one-time usage)
- Authorization with gateway enforcement

Available via ``client.execution_gateway.*``.

Backend endpoints
-----------------
- POST /api/v1/execution/authorize
- POST /api/v1/execution/verify
- POST /api/v1/execution/consume
- GET  /api/v1/execution/policies
- POST /api/v1/execution/policies
- GET  /api/v1/execution/receipts/{receipt_id}
- POST /api/v1/execution/simulations
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, List

if TYPE_CHECKING:
    from blocklog.client import BlocklogClient


class ExecutionGatewayClient:
    """Execution gateway client for risk-aware authorization and token management.

    Provides high-level access to the execution gateway which:
    - Evaluates policies with risk scoring (0-100 scale)
    - Creates signed execution tokens
    - Tracks token consumption (one-time usage)
    - Maintains governance records (risk assessments, policy evaluations)

    Accessed as ``client.execution_gateway``.

    Examples
    --------
    >>> # Authorize an execution with risk scoring
    >>> result = client.execution_gateway.authorize(
    ...     processor="payment",
    ...     action_type="transfer",
    ...     amount_minor=500000,
    ...     currency="USD",
    ...     execution_reference="tx_123"
    ... )
    >>> print(result["outcome"]["risk_score"])  # e.g., 45
    >>> print(result["outcome"]["risk_level"])   # "MEDIUM"
    >>> print(result["token"])                   # signed token string

    >>> # Verify and consume a token
    >>> result = client.execution_gateway.verify_and_consume(
    ...     token=result["token"],
    ...     execution_reference="tx_123"
    ... )
    >>> print(result["token_consumed"])  # True

    >>> # Get risk assessment
    >>> assessments = client.execution_gateway.list_risk_assessments(
    ...     risk_level="HIGH",
    ...     limit=50
    ... )
    """

    def __init__(self, client: BlocklogClient) -> None:
        self._client = client

    # ── Authorization ────────────────────────────────────────────────────────

    def authorize(
        self,
        processor: str,
        action_type: str,
        amount_minor: int = 0,
        currency: str = "USD",
        destination: Optional[str] = None,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        subject_reference: Optional[str] = None,
        transaction_reference: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        approval: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Authorize an execution through the gateway with policy evaluation.

        The gateway evaluates all matching policies, calculates risk scores,
        and returns a signed execution token if authorized.

        Parameters
        ----------
        processor:
            Processor name (e.g., "payment", "transfer", "trade").
        action_type:
            Type of action being performed.
        amount_minor:
            Amount in minor currency units (e.g., cents).
        currency:
            Currency code (e.g., "USD", "EUR").
        destination:
            Optional destination (account, wallet, etc.).
        trace_id:
            Optional trace ID for distributed tracing.
        session_id:
            Optional session ID for workflow tracking.
        workflow_id:
            Optional workflow ID.
        idempotency_key:
            Optional key for idempotent requests.
        subject_reference:
            Optional subject reference.
        transaction_reference:
            Optional transaction reference.
        context:
            Optional execution context.
        approval:
            Optional human approval information.

        Returns
        -------
        dict
            Contains:
            - ``token``: Signed execution token (null if denied)
            - ``token_id``: Internal token UUID
            - ``token_expires_at``: Expiration timestamp
            - ``receipt_id``: Receipt UUID
            - ``receipt_signature``: Receipt signature
            - ``status``: Token status ("ISSUED" or "DENIED")
            - ``outcome``: Authorization outcome with:
              - ``decision``: "APPROVED" or "DENIED"
              - ``reasons``: List of failure reasons
              - ``risk_score``: Risk score (0-100)
              - ``risk_level``: "LOW", "MEDIUM", "HIGH", or "CRITICAL"
              - ``risk_factors``: Detailed risk factors
              - ``policy_id``: Matching policy UUID
              - ``policy_hash``: Policy hash
              - ``shadow_mode``: Whether policy is in shadow mode

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails.
        """
        payload = {
            "processor": processor,
            "action_type": action_type,
            "amount_minor": amount_minor,
            "currency": currency,
            "destination": destination,
            "trace_id": trace_id,
            "session_id": session_id,
            "workflow_id": workflow_id,
            "idempotency_key": idempotency_key,
            "subject_reference": subject_reference,
            "transaction_reference": transaction_reference,
            "context": context,
            "approval": approval,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", "/execution/authorize", json=payload
            )
        )

    def verify(self, token: str, enforce: bool = True) -> dict[str, Any]:
        """
        Verify an execution token and return authorization status.

        Parameters
        ----------
        token:
            The signed execution token from authorize().
        enforce:
            Whether to enforce policy (default: True).
            When False, shadow mode policies are not enforced.

        Returns
        -------
        dict
            Contains:
            - ``authorized``: Whether token is valid
            - ``token_id``: Internal token UUID
            - ``receipt_id``: Receipt UUID
            - ``status``: Verification status
            - ``reasons``: List of failure reasons (empty if authorized)
            - ``shadow_mode``: Whether policy is in shadow mode
            - ``expires_at``: Token expiration timestamp

        Raises
        ------
        httpx.HTTPStatusError
            If the token is invalid or expired.
        """
        payload = {
            "token": token,
            "enforce": enforce,
        }

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", "/execution/verify", json=payload
            )
        )

    # ── Consumption (PHASE 3) ────────────────────────────────────────────────

    def consume(
        self,
        token: str,
        processor: str,
        action_type: str,
        execution_reference: Optional[str] = None,
        transaction_reference: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Consume an execution token - enforces one-time usage.

        Tokens can only be consumed once. Subsequent consumption attempts
        return a 409 Conflict error.

        Parameters
        ----------
        token:
            The signed execution token to consume.
        processor:
            Processor name (must match authorization).
        action_type:
            Action type (must match authorization).
        execution_reference:
            Optional execution reference for tracking.
        transaction_reference:
            Optional transaction reference.

        Returns
        -------
        dict
            Contains:
            - ``consumed_at``: Timestamp of consumption
            - ``token_consumed``: True
            - ``execution_reference``: Provided reference
            - ``token_id``: Internal token UUID
            - ``status``: "CONSUMED"

        Raises
        ------
        httpx.HTTPStatusError
            - 404: Token not found
            - 409: Token already consumed
            - 401: Token expired

        Examples
        --------
        >>> result = client.execution_gateway.authorize(...)
        >>> # ... use token in external system ...
        >>> # After successful external processing:
        >>> consumption = client.execution_gateway.consume(
        ...     token=result["token"],
        ...     execution_reference="ext_tx_123"
        ... )
        """
        payload = {
            "token": token,
            "processor": processor,
            "action_type": action_type,
            "execution_reference": execution_reference,
            "transaction_reference": transaction_reference,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", "/execution/consume", json=payload
            )
        )

    # ── Risk Assessment (PHASE 2) ────────────────────────────────────────────

    def calculate_risk(
        self,
        action_type: str,
        amount_minor: int,
        currency: str = "USD",
        destination: Optional[str] = None,
        agent_trust_level: Optional[str] = None,
        delegation_depth: int = 1,
        context_stale: bool = False,
        policy_violations: int = 0,
        amount_thresholds: Optional[dict[str, int]] = None,
    ) -> dict[str, Any]:
        """
        Calculate risk score for an action.

        This is the same scoring logic used by the gateway during
        policy evaluation. Useful for pre-screening before execution.

        Parameters
        ----------
        action_type:
            Type of action being performed.
        amount_minor:
            Amount in minor currency units.
        currency:
            Currency code.
        destination:
            Optional destination.
        agent_trust_level:
            Trust level of agent ("LOW", "MEDIUM", "HIGH", "CRITICAL").
        delegation_depth:
            Depth of delegation chain.
        context_stale:
            Whether context is stale.
        policy_violations:
            Number of policy violations found.
        amount_thresholds:
            Custom amount thresholds. Default:
            - medium: 100000 (default units)
            - high: 500000
            - critical: 1000000

        Returns
        -------
        dict
            Contains:
            - ``risk_score``: Risk score (0-100)
            - ``risk_level``: "LOW", "MEDIUM", "HIGH", or "CRITICAL"
            - ``risk_factors``: Detailed factors contributing to risk

        Examples
        --------
        >>> risk = client.execution_gateway.calculate_risk(
        ...     action_type="transfer",
        ...     amount_minor=750000,  # 7500 units
        ...     destination=None,      # Unknown destination
        ...     delegation_depth=4,
        ...     context_stale=True,
        ... )
        >>> print(f"Risk: {risk['risk_score']} ({risk['risk_level']})")
        >>> print(f"Factors: {risk['risk_factors']}")
        """
        payload = {
            "action_type": action_type,
            "amount_minor": amount_minor,
            "currency": currency,
            "destination": destination,
            "agent_trust_level": agent_trust_level,
            "delegation_depth": delegation_depth,
            "context_stale": context_stale,
            "policy_violations": policy_violations,
            "amount_thresholds": amount_thresholds,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        # Risk calculation is handled server-side in gateway
        # This method can be used to verify risk logic matches expectations
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "POST", "/execution/simulations", json=payload
            )
        )

    # ── Policy Management ────────────────────────────────────────────────────

    def list_policies(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """
        List all execution policies.

        Parameters
        ----------
        limit:
            Maximum number of policies to return.
        offset:
            Pagination offset.

        Returns
        -------
        dict
            Contains ``items`` array of policy objects.
        """
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", "/execution/policies", params={"limit": limit, "offset": offset}
            )
        )

    def get_policy(self, policy_id: str) -> dict[str, Any]:
        """
        Get a specific policy by ID.

        Parameters
        ----------
        policy_id:
            UUID of the policy.

        Returns
        -------
        dict
            Policy object with all configuration.
        """
        return self._client.retry.run(
            lambda: self._client.transport.request("GET", f"/execution/policies/{policy_id}")
        )

    # ── Receipts ─────────────────────────────────────────────────────────────

    def verify_receipt(
        self,
        receipt_json: str,
        public_key: Optional[str] = None,
        verify_signature: bool = True,
        verify_merkle: bool = True,
    ) -> dict[str, Any]:
        """
        Verify an execution receipt cryptographically.

        This method performs standalone verification of a receipt without
        requiring database access. It validates:
        - Canonical hash integrity
        - Ed25519 signature (if public_key provided)
        - Merkle proof (if included)

        Parameters
        ----------
        receipt_json:
            JSON string of the receipt to verify.
        public_key:
            Ed25519 public key in hex (64 chars) or base64 format.
            Required for signature verification.
        verify_signature:
            Whether to verify the Ed25519 signature.
        verify_merkle:
            Whether to verify the Merkle inclusion proof.

        Returns
        -------
        dict
            Verification result with:
            - ``successful``: bool
            - ``errors``: List of error messages
            - ``warnings``: List of warning messages
            - ``receipt_id``: Optional receipt ID
            - ``verified_at``: ISO timestamp
        """
        from blocklog.api.receipt_verification import ReceiptVerificationClient

        verifier = ReceiptVerificationClient(public_key=public_key)
        return verifier.verify_receipt(
            receipt_json=receipt_json,
            verify_signature=verify_signature,
            verify_merkle=verify_merkle,
        )

    def get_receipt(self, receipt_id: str) -> dict[str, Any]:
        """
        Get an execution receipt.

        Receipts are immutable records of authorization and verification events.
        Each signed token corresponds to multiple receipts (ISSUED, VERIFIED,
        CONSUMED, EXPIRED, etc.).

        Parameters
        ----------
        receipt_id:
            UUID of the receipt.

        Returns
        -------
        dict
            Receipt object with:
            - ``id``: Receipt UUID
            - ``token_id``: Associated token UUID
            - ``receipt_type``: "ISSUED", "VERIFIED", "CONSUMED", etc.
            - ``status``: Current status
            - ``receipt_hash``: SHA-256 hash of receipt payload
            - ``signature``: Ed25519 signature
            - ``created_at``: Timestamp
        """
        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", f"/execution/receipts/{receipt_id}"
            )
        )

    def list_receipts(
        self,
        status: Optional[str] = None,
        policy_id: Optional[str] = None,
        processor: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        List execution receipts with filtering.

        Parameters
        ----------
        status:
            Filter by status (ISSUED, VERIFIED, CONSUMED, EXPIRED, REVOKED).
        policy_id:
            Filter by policy ID.
        processor:
            Filter by processor name.
        limit:
            Maximum number of receipts to return (max 1000).
        offset:
            Number of receipts to skip for pagination.

        Returns
        -------
        list[dict[str, Any]]
            List of receipt objects matching filters.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if policy_id:
            params["policy_id"] = policy_id
        if processor:
            params["processor"] = processor

        return self._client.retry.run(
            lambda: self._client.transport.request(
                "GET", "/execution/receipts", params=params
            )
        )
