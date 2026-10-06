"""
Receipt Verification Client

Provides high-level API for cryptographic receipt verification.
The actual verification logic is in receipt_verifier.py.
"""
from typing import Optional, Dict, Any

from blocklog.api.receipt_verifier import (
    ReceiptVerifier,
    verify_receipt_standalone,
    verify_receipt_file,
)


class ReceiptVerificationClient:
    """
    Client for cryptographic receipt verification.
    
    This client provides independent verification of execution receipts
    without requiring database access.
    
    Examples:
        >>> from blocklog import ReceiptVerificationClient
        >>> verifier = ReceiptVerificationClient()
        >>> result = verifier.verify_receipt(receipt_json, public_key="...")
        >>> if result.successful:
        ...     print("Receipt is valid!")
    """
    
    def __init__(self, public_key: Optional[str] = None):
        """
        Initialize the receipt verification client.
        
        Args:
            public_key: Ed25519 public key in hex or base64 format (optional)
        """
        self.verifier = ReceiptVerifier(public_key=public_key)
    
    def verify_receipt(
        self,
        receipt_json: str,
        public_key: Optional[str] = None,
        verify_signature: bool = True,
        verify_merkle: bool = True,
    ) -> Dict[str, Any]:
        """
        Verify a receipt from JSON string.
        
        Args:
            receipt_json: JSON string of the receipt
            public_key: Ed25519 public key (overrides instance's key)
            verify_signature: Verify Ed25519 signature
            verify_merkle: Verify Merkle proof
            
        Returns:
            Dictionary with verification result containing:
                - successful: bool
                - errors: List[str]
                - warnings: List[str]
                - receipt_id: Optional[str]
                - verified_at: Optional[str]
        """
        return verify_receipt_standalone(
            receipt_json=receipt_json,
            public_key=public_key,
            verify_signature=verify_signature,
            verify_merkle=verify_merkle,
        )
    
    def verify_receipt_file(
        self,
        filepath: str,
        public_key: Optional[str] = None,
        verify_signature: bool = True,
        verify_merkle: bool = True,
    ) -> Dict[str, Any]:
        """
        Verify a receipt from a JSON file.
        
        Args:
            filepath: Path to JSON file containing the receipt
            public_key: Ed25519 public key (overrides instance's key)
            verify_signature: Verify Ed25519 signature
            verify_merkle: Verify Merkle proof
            
        Returns:
            Dictionary with verification result
        """
        return verify_receipt_file(
            filepath=filepath,
            public_key=public_key,
            verify_signature=verify_signature,
            verify_merkle=verify_merkle,
        )
    
    def verify_signature(
        self,
        receipt_json: str,
        public_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify only the Ed25519 signature of a receipt.
        
        Args:
            receipt_json: JSON string of the receipt
            public_key: Ed25519 public key (overrides instance's key)
            
        Returns:
            Dictionary with signature verification result
        """
        return verify_receipt_standalone(
            receipt_json=receipt_json,
            public_key=public_key,
            verify_signature=True,
            verify_merkle=False,
        )
    
    def verify_integrity(
        self,
        receipt_json: str,
    ) -> Dict[str, Any]:
        """
        Verify only the canonical hash integrity of a receipt.
        
        Args:
            receipt_json: JSON string of the receipt
            
        Returns:
            Dictionary with hash verification result
        """
        return verify_receipt_standalone(
            receipt_json=receipt_json,
            public_key=None,
            verify_signature=False,
            verify_merkle=False,
        )


# Type hints for better IDE support
ReceiptVerificationResult = Dict[str, Any]
