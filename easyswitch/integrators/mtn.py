"""
EasySwitch - MTN Mobile Money Integrator
"""
import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from easyswitch.adapters.base import BaseAdapter
from easyswitch.conf.config import Config
from easyswitch.exceptions import (APIError, AuthenticationError,
                                   TransactionNotFoundError,
                                   UnsupportedOperationError)
from easyswitch.types import (Currency, CustomerInfo, PaymentResponse,
                              Provider, TransactionStatus, TransactionType)
from easyswitch.utils.http import HTTPClient


class MTNIntegrator(BaseAdapter):
    """Integrator for MTN Mobile Money API."""
    
    def __init__(self, config: Config):
        """
        Initialize the MTN integrator.
        
        Args:
            config: Configuration du SDK
        """
        super().__init__(config)
        self.api_key = config.mtn_api_key
        self.api_secret = config.mtn_api_secret
        self.app_id = config.mtn_app_id
        self.callback_url = config.mtn_callback_url
        
        # Token d'authentification et sa date d'expiration
        self._auth_token = None
        self._token_expires_at = None
        
        # Initialiser le client HTTP
        self.http_client = HTTPClient(
            base_url=config.get_api_url("mtn"),
            default_headers={
                "Ocp-Apim-Subscription-Key": self.api_key,
                "X-Reference-Id": self.app_id or str(uuid.uuid4())
            },
            timeout=config.timeout,
            debug=config.debug
        )
    
    async def _ensure_auth_token(self) -> str:
        """
        S'assure que nous avons un token d'authentification valide.
        
        Returns:
            str: Token d'authentification valide
        """
        now = datetime.now()
        
        # If token doesn't exist or is expired, request a new one
        if not self._auth_token or not self._token_expires_at or self._token_expires_at <= now:
            try:
                # Generate ephemeral key pair for authentication
                subscription_key = self.api_key
                
                # Obtenir le token d'authentification
                response = await self.http_client.post(
                    "collection/token/",
                    json_data={
                        "grant_type": "client_credentials"
                    },
                    headers={
                        "Authorization": f"Basic {base64.b64encode(f'{self.app_id}:{self.api_secret}'.encode()).decode()}"
                    }
                )
                
                if "access_token" not in response:
                    raise AuthenticationError("MTN authentication token not received")
                
                self._auth_token = response["access_token"]
                # Token valid for 1h (3600 sec)
                expires_in = int(response.get("expires_in", 3600))
                self._token_expires_at = now + timedelta(seconds=expires_in - 60)  # 60 sec margin
                
            except Exception as e:
                raise AuthenticationError(f"MTN authentication error: {str(e)}")
        
        return self._auth_token
    
    async def send_payment(
        self,
        amount: float,
        phone_number: str,
        currency: Currency,
        reference: str,
        customer_info: Optional[CustomerInfo] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResponse:
        """
        Sends an MTN Mobile Money payment request.
        
        Args:
            amount: Amount to pay
            phone_number: Customer phone number (international format)
            currency: Payment currency
            reference: Unique reference for the payment
            customer_info: Additional customer information
            metadata: Custom metadata
            
        Returns:
            PaymentResponse: Payment request response
        """
        # Ensure we have a valid token
        auth_token = await self._ensure_auth_token()
        
        # Format phone number (remove +, spaces, etc.)
        clean_phone = phone_number.replace("+", "").replace(" ", "")
        
        # Generate UUID for transaction
        transaction_id = str(uuid.uuid4())
        external_id = reference or str(uuid.uuid4())
        
        # Prepare request
        payload = {
            "amount": str(amount),
            "currency": currency.value,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": clean_phone
            },
            "payerMessage": "Payment via EasySwitch",
            "payeeNote": "Payment via EasySwitch"
        }
        
        # Add metadata if provided
        if metadata:
            payload["metadata"] = metadata
        
        try:
            # Perform payment request
            response = await self.http_client.post(
                f"collection/v1_0/requesttopay",
                json_data=payload,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Reference-Id": transaction_id,
                    "X-Callback-Url": self.callback_url
                }
            )
            
            # MTN usually returns a 202 Accepted without response body
            # Status must be checked separately
            payment_response = PaymentResponse(
                transaction_id=transaction_id,
                provider=Provider.MTN,
                status=TransactionStatus.PENDING,
                amount=amount,
                currency=currency,
                reference=external_id,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=10),
                customer=customer_info,
                metadata=metadata or {},
                raw_response=response if isinstance(response, dict) else {}
            )
            
            return payment_response
            
        except APIError as e:
            # Handle MTN-specific errors
            raise APIError(
                message=f"MTN error during payment request: {str(e)}",
                status_code=e.status_code,
                provider="mtn",
                raw_response=e.raw_response
            )
    
    async def check_status(self, transaction_id: str) -> TransactionStatus:
        """
        Checks the status of an MTN transaction.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            TransactionStatus: Current transaction status
        """
        # Ensure we have a valid token
        auth_token = await self._ensure_auth_token()
        
        try:
            # Perform verification request
            response = await self.http_client.get(
                f"collection/v1_0/requesttopay/{transaction_id}",
                headers={
                    "Authorization": f"Bearer {auth_token}"
                }
            )
            
            # Map MTN status to our TransactionStatus enum
            mtn_status = response.get("status", "").lower()
            status_mapping = {
                "pending": TransactionStatus.PENDING,
                "successful": TransactionStatus.SUCCESSFUL,
                "failed": TransactionStatus.FAILED,
                "cancelled": TransactionStatus.CANCELLED,
                "ongoing": TransactionStatus.PROCESSING,
                "rejected": TransactionStatus.FAILED,
                "timeout": TransactionStatus.EXPIRED
            }
            
            return status_mapping.get(mtn_status, TransactionStatus.PENDING)
            
        except APIError as e:
            if e.status_code == 404:
                raise TransactionNotFoundError(f"MTN transaction not found: {transaction_id}")
            
            raise APIError(
                message=f"MTN error during status check: {str(e)}",
                status_code=e.status_code,
                provider="mtn",
                raw_response=e.raw_response
            )
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """
        Cancels an MTN transaction if possible.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            bool: True if cancellation succeeded, False otherwise
        """
        # MTN doesn't support cancellation via API
        raise UnsupportedOperationError("Transaction cancellation is not supported by MTN Mobile Money")
    
    async def refund(
        self,
        transaction_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> PaymentResponse:
        """
        Performs a refund for an MTN transaction.
        
        Args:
            transaction_id: Transaction identifier
            amount: Amount to refund (if None, refunds the total amount)
            reason: Refund reason
            
        Returns:
            PaymentResponse: Refund request response
        """
        # Ensure we have a valid token
        auth_token = await self._ensure_auth_token()
        
        # First check the status of the initial transaction
        status = await self.check_status(transaction_id)
        if status != TransactionStatus.SUCCESSFUL:
            raise APIError(
                message=f"Cannot refund an unsuccessful transaction (status: {status})",
                provider="mtn"
            )
        
        # Retrieve transaction details to know the initial amount
        try:
            response = await self.http_client.get(
                f"collection/v1_0/requesttopay/{transaction_id}",
                headers={
                    "Authorization": f"Bearer {auth_token}"
                }
            )
            
            original_amount = float(response.get("amount", "0"))
            currency = Currency(response.get("currency", "XOF"))
            payer_id = response.get("payer", {}).get("partyId")
            
            if not amount:
                amount = original_amount
            
            if amount > original_amount:
                raise ValueError(f"Refund amount ({amount}) cannot exceed initial amount ({original_amount})")
            
            # Create ID for refund
            refund_id = str(uuid.uuid4())
            
            # Prepare refund request
            payload = {
                "amount": str(amount),
                "currency": currency.value,
                "externalId": f"refund-{transaction_id}",
                "payee": {
                    "partyIdType": "MSISDN",
                    "partyId": payer_id
                },
                "payerMessage": reason or "Refund via EasySwitch",
                "payeeNote": reason or "Refund via EasySwitch"
            }
            
            # Perform refund request
            await self.http_client.post(
                "disbursement/v1_0/transfer",
                json_data=payload,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Reference-Id": refund_id,
                    "X-Callback-Url": self.callback_url
                }
            )
            
            return PaymentResponse(
                transaction_id=refund_id,
                provider=Provider.MTN,
                status=TransactionStatus.PENDING,
                amount=amount,
                currency=currency,
                reference=f"refund-{transaction_id}",
                created_at=datetime.now(),
                raw_response=response
            )
            
        except APIError as e:
            if e.status_code == 404:
                raise TransactionNotFoundError(f"MTN transaction not found: {transaction_id}")
            
            raise APIError(
                message=f"MTN error during refund: {str(e)}",
                status_code=e.status_code,
                provider="mtn",
                raw_response=e.raw_response
            )
    
    async def validate_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """
        Validates an incoming MTN webhook.
        
        Args:
            payload: Webhook content
            headers: Request headers
            
        Returns:
            bool: True if webhook is valid, False otherwise
        """
        # MTN usually uses token-based validation
        notification_token = headers.get("X-Notification-Token")
        if not notification_token:
            return False
        
        # Verify signature (simplified example)
        expected_signature = hmac.new(
            self.api_secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        return notification_token == expected_signature
    
    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyzes an MTN webhook and converts it to standardized format.
        
        Args:
            payload: Webhook content
            headers: Request headers
            
        Returns:
            Dict[str, Any]: Standardized webhook data
        """
        # Verify that the webhook is valid
        if not await self.validate_webhook(payload, headers):
            raise ValueError("Invalid MTN webhook")
        
        # Extract important data
        transaction_id = payload.get("referenceId")
        status = payload.get("status", "").lower()
        
        # Map MTN status to our TransactionStatus enum
        status_mapping = {
            "successful": TransactionStatus.SUCCESSFUL,
            "failed": TransactionStatus.FAILED,
            "rejected": TransactionStatus.FAILED,
            "timeout": TransactionStatus.EXPIRED,
            "pending": TransactionStatus.PENDING,
            "ongoing": TransactionStatus.PROCESSING
        }
        
        transaction_status = status_mapping.get(status, TransactionStatus.PENDING)
        
        return {
            "transaction_id": transaction_id,
            "provider": Provider.MTN,
            "status": transaction_status,
            "raw_data": payload
        }