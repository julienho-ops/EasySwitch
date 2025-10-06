"""
EasySwitch - Paystack Integrator
"""

import hmac
import hashlib
from typing import ClassVar, List, Dict, Optional, Any

from easyswitch.adapters.base import AdaptersRegistry, BaseAdapter
from easyswitch.types import (Currency, PaymentResponse, 
                              TransactionDetail,TransactionStatusResponse,)
from easyswitch.exceptions import  PaymentError,UnsupportedOperationError


@AdaptersRegistry.register()
class PaystackAdapter(BaseAdapter):
    """Paystack Adapter for EasySwitch SDK."""
    
    SANDBOX_URL: str = "https://api.paystack.co"
    PRODUCTION_URL: str = "https://api.paystack.co"

    SUPPORTED_CURRENCIES: ClassVar[List[Currency]] = [
        Currency.NGN,
        Currency.GHS,
        Currency.USD,
    ]

    MIN_AMOUNT: ClassVar[Dict[Currency, float]] = {
        Currency.NGN: 50.0,    # 50.00 NGN (main units)
        Currency.GHS: 0.10,    # 0.10 GHS
        Currency.USD: 2.0,     # 2.00 USD
    }

    MAX_AMOUNT: ClassVar[Dict[Currency, float]] = {
        Currency.NGN: 10_000_000,
        Currency.GHS: 10_000_000,
        Currency.USD: 10_000_000,
    }

    def validate_credentials(self) -> bool:
        """Validate the credentials for Paystack."""
        return bool(self.config.api_key)

    def get_credentials(self):
        """Return API credentials."""
        return {"api_key": self.config.api_key}

    def get_headers(self, authorization=True, **kwargs) -> Dict[str, str]:
        """Return headers for Paystack requests."""
        headers = {"Content-Type": "application/json"}
        if authorization:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

        # validate_webhook expects raw_body: bytes
    def validate_webhook(self, raw_body: bytes, headers: Dict[str, str]) -> bool:
        signature = headers.get("x-paystack-signature")
        secret_key = getattr(self.config, "api_key", None)
        if not signature or not secret_key:
            return False

        computed_sig = hmac.new(secret_key.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed_sig, signature)


    def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Parse Paystack webhook into a normalized format."""
        data = payload.get("data", {})
        event = payload.get("event")

        return {
            "transaction_id": data.get("reference"),
            "provider": self.provider_name(),
            "status": self.get_normalize_status(data.get("status")),
            "event": event,
            "amount": data.get("amount", 0) / 100,
            "currency": data.get("currency", "NGN"),
            "customer_email": data.get("customer", {}).get("email"),
            "raw_data": payload,
        }
    
    async def send_payment(self, transaction: TransactionDetail) -> PaymentResponse:
        """Send a payment initialization request to Paystack."""
        self.validate_transaction(transaction)

        payload = {
            "amount": int(transaction.amount * 100),  # Paystack expects smallest unit
            "email": transaction.customer.email,
            "reference": transaction.reference,
            "callback_url": transaction.callback_url or self.config.callback_url,
            "metadata": transaction.metadata or {},
        }

        async with self.get_client() as client:
            response = await client.post(
                "/transaction/initialize",
                json=payload,
                headers=self.get_headers()
            )

            data = response.json() if hasattr(response, "json") else response.data
            if response.status in range(200, 300) and data.get("status"):
                init_data = data.get("data", {})
                return PaymentResponse(
                    transaction_id=transaction.transaction_id,
                    reference=init_data.get("reference"),
                    provider=self.provider_name(),
                    status="pending",
                    amount=transaction.amount,
                    currency=transaction.currency,
                    payment_link=init_data.get("authorization_url"),
                    transaction_token=init_data.get("access_code"),
                    metadata=init_data,
                    raw_response=data,
                )

            raise PaymentError(
                message=f"Payment request failed with status {response.status}",
                status_code=response.status,
                raw_response=data,
            )

    async def check_status(self, reference: str) -> TransactionStatusResponse:
        """Check the status of a Paystack transaction by reference."""
        async with self.get_client() as client:
            response = await client.get(
                f"/transaction/verify/{reference}",
                headers=self.get_headers()
            )

            data = response.json() if hasattr(response, "json") else response.data
            if not data.get("status"):
                raise PaymentError(
                    message="Failed to verify Paystack transaction",
                    raw_response=data
                )

            tx = data.get("data", {})
            return TransactionStatusResponse(
                transaction_id=tx.get("id"),
                provider=self.provider_name(),
                status=self.get_normalize_status(tx.get("status")),
                amount=(tx.get("amount") or 0) / 100,
                data=tx,
            )

    async def cancel_transaction(self, transaction_id: str) -> None:
        """Paystack does not support transaction cancellation.
            Use refund() for post-payment reversals.
        """
        raise UnsupportedOperationError(
            self.provider_name(),
        )

    async def refund(self, transaction_id: str, amount: Optional[float] = None) -> PaymentResponse:
        """Refund a Paystack transaction."""
        async with self.get_client() as client:
            payload = {"transaction": transaction_id}
            if amount:
                payload["amount"] = int(amount * 100)  

            response = await client.post("/refund", json=payload, headers=self.get_headers())

            data = response.json() if hasattr(response, "json") else response.data
            if response.status in range(200, 300) and data.get("status"):
                refund_data = data.get("data", {})
                return PaymentResponse(
                    transaction_id=transaction_id,
                    reference=refund_data.get("transaction", {}).get("reference", f"refund-{transaction_id}"),
                    provider=self.provider_name(),
                    status=self.get_normalize_status(refund_data.get("status")),
                    amount=(refund_data.get("amount") or (amount or 0)) / 100,
                    currency=refund_data.get("currency", "NGN"),
                    metadata=refund_data,
                    raw_response=data,
                )

            raise PaymentError(
                message=f"Refund failed with status {response.status}",
                status_code=response.status,
                raw_response=data,
            )
        
    async def get_transaction_detail(self, transaction_id: str) -> PaymentResponse:
        """Retrieve transaction details from Paystack by transaction ID."""
        async with self.get_client() as client:
            response = await client.get(f"/transaction/{transaction_id}", headers=self.get_headers())

            data = response.json() if hasattr(response, "json") else response.data
            if response.status in range(200, 300) and data.get("status"):
                tx = data.get("data", {})
                return PaymentResponse(
                    transaction_id=str(tx.get("id", transaction_id)),
                    reference=tx.get("reference"),
                    provider=self.provider_name(),
                    status=self.get_normalize_status(tx.get("status")),
                    amount=tx.get("amount", 0) / 100,
                    currency=tx.get("currency", "NGN"),
                    metadata=tx.get("metadata", {}),
                    raw_response=tx
                )

            raise PaymentError(
                message=f"Failed to retrieve transaction {transaction_id}",
                status_code=response.status,
                raw_response=data
            )
