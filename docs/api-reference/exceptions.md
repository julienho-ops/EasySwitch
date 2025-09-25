# ⚠️ Exception Handling in EasySwitch

EasySwitch defines a **hierarchy of custom exceptions** to provide clear and structured error handling.
Instead of catching generic Python exceptions, you can catch **specific errors** raised by the SDK or providers.

This makes it easier to:

* Handle provider-specific failures.
* Distinguish between **configuration issues**, **API failures**, and **validation errors**.
* Implement robust retry and fallback strategies.

---

## 🔹 Exception Hierarchy

```
Exception
└── EasySwitchError
    ├── ConfigurationError
    ├── AuthenticationError
    ├── InvalidRequestError
    ├── ValidationError
    ├── NetworkError
    ├── InvalidProviderError
    ├── TransactionNotFoundError
    ├── WebhookValidationError
    ├── UnsupportedOperationError
    ├── APIError
    │   ├── RateLimitError
    │   ├── PaymentError
    │   ├── WebhookError
    │   ├── CustomerError
    │   ├── CurrencyError
    │   ├── RefundError
    │   ├── CancellationError
    │   ├── BalanceError
    │   └── LogError
```

---

## 🔹 `EasySwitchError`

The **base exception** for the SDK.
All other errors inherit from this class.

```python
class EasySwitchError(Exception):
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
```

✅ Attributes:

* `message` → Human-readable description of the error.
* `code` → Short identifier for the error (optional).
* `details` → Dict with structured information about the error.

---

## 🔹 Configuration & Authentication Errors

* **`ConfigurationError`** → Misconfigured SDK or provider settings.

  * Example: Missing API key or wrong environment value.

* **`AuthenticationError`** → Failed authentication with the provider.

  * Example: Invalid API key/secret.

* **`InvalidRequestError`** → Request built incorrectly before being sent.

  * Example: Missing required parameters.

* **`ValidationError`** → A specific request field is invalid.

  * Extra field: `field` → name of the invalid field.

```python
try:
    client = EasySwitchClient(config={})
except ConfigurationError as e:
    print(f"Invalid configuration: {e.message}")
```

---

## 🔹 API Errors

`APIError` is the **base class** for provider-related failures.
It contains extra metadata to help debugging:

✅ Attributes:

* `status_code` → HTTP status code (if available).
* `provider` → Provider name (e.g. `"mtn"`, `"wave"`).
* `raw_response` → Full API response from provider.

Subclasses of `APIError`:

* **`RateLimitError`** → Too many requests sent in a short time.
* **`PaymentError`** → Error during payment processing.
* **`RefundError`** → Refund request failed.
* **`CancellationError`** → Transaction cancellation failed.
* **`WebhookError`** → Error while processing a webhook.
* **`CustomerError`** → Customer creation/management failure.
* **`CurrencyError`** → Unsupported or invalid currency.
* **`BalanceError`** → Balance retrieval failed.
* **`LogError`** → Error related to logging or audit logs.

```python
try:
    payment = client.send_payment(transaction)
except PaymentError as e:
    print(f"Payment failed: {e.details.get('raw_response')}")
```

---

## 🔹 Network & Provider Errors

* **`NetworkError`** → Communication failure (timeout, DNS issue).
* **`InvalidProviderError`** → The requested provider is not supported or not registered.
* **`TransactionNotFoundError`** → Transaction ID does not exist in provider records.
* **`WebhookValidationError`** → Invalid or spoofed webhook payload.
* **`UnsupportedOperationError`** → The provider does not support a requested operation (e.g., cancellation not available).

```python
try:
    status = client.check_status("invalid_id")
except TransactionNotFoundError:
    print("Transaction does not exist")
```

---

## 🔹 Example – Global Error Handling

```python
from easyswitch.exceptions import *

try:
    client.send_payment(transaction)

except ConfigurationError as e:
    print(f"Bad SDK configuration: {e.details}")

except AuthenticationError:
    print("Authentication failed with provider")

except RateLimitError:
    print("Too many requests, please retry later")

except PaymentError as e:
    print(f"Payment failed: {e.message}, response: {e.details.get('raw_response')}")

except EasySwitchError as e:
    print(f"Unexpected EasySwitch error: {e.message}")

except Exception as e:
    print(f"Unexpected Python error: {str(e)}")
```

---

## ✅ Best Practices

* Always catch **specific exceptions** when possible (e.g., `PaymentError`).
* Use `EasySwitchError` as a **generic fallback**.
* Log `details` for debugging (contains raw provider response).
* In production, map exceptions to **user-friendly messages** (e.g., `"Your payment could not be processed, please try again"`).
