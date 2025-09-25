# Base Adapter (`easyswitch.adapters.base`)

This module provides the **foundation of EasySwitch’s adapter system**.

* An **adapter** is a small class that knows how to talk to a specific **payment provider (aggregator)**.
* Each adapter implements the same **common interface**, so that EasySwitch can interact with **any provider** in a consistent way.
* The **adapter registry** keeps track of all registered providers, so you can dynamically load them at runtime.

---

## 🔹 `AdaptersRegistry`

The registry is the **central directory of all adapters**.
Instead of hardcoding adapter classes, EasySwitch lets you **register** and **retrieve** them dynamically.

Think of it as a plugin manager:

* Developers implement an adapter for a new provider.
* They register it under a **provider name**.
* Later, EasySwitch can fetch it by name and use it.

### Methods

#### `AdaptersRegistry.register(name: Optional[str] = None)`

Decorator used to register an adapter under the given name.

* If `name` is provided → adapter is registered under that name.
* If omitted → EasySwitch will use the adapter class name (`SemoaAdapter → semoa`).

```python
@AdaptersRegistry.register("semoa")
class SemoaAdapter(BaseAdapter):
    ...
```

This means you can later do:

```python
adapter_cls = AdaptersRegistry.get("semoa")
adapter = adapter_cls(config=my_provider_config)
```

---

#### `AdaptersRegistry.get(name: str) -> Type[BaseAdapter]`

Fetches an adapter by name.

* If found → returns the adapter **class** (not an instance).
* If not found → raises `InvalidProviderError`.

---

#### `AdaptersRegistry.all() -> List[Type[BaseAdapter]]`

Returns a list of **all registered adapter classes**.
Useful for debugging or auto-loading providers.

---

#### `AdaptersRegistry.list() -> List[str]`

Returns just the **names** of all registered adapters.

```python
print(AdaptersRegistry.list())
# ["semoa", "wave", "mtn", ...]
```

---

#### `AdaptersRegistry.clear() -> None`

Removes all registered adapters (used in tests).

---

## 🔹 `BaseAdapter`

The **abstract base class** for all adapters.
Every provider must implement this interface to ensure consistency across EasySwitch.

It defines:

* ✅ Common configuration logic (sandbox/production, client setup).
* ✅ Utility methods (validation, required fields, formatting).
* ✅ Abstract methods that **MUST** be implemented per provider.

---

### Class Attributes

* `REQUIRED_FIELDS: List[str]` → List of required fields (ex: `["api_key", "merchant_id"]`).
* `SANDBOX_URL: str` → Provider sandbox base URL.
* `PRODUCTION_URL: str` → Provider production base URL.
* `SUPPORTED_CURRENCIES: List[Currency]` → Currencies supported by the provider.
* `MIN_AMOUNT: Dict[Currency, float]` → Minimum transaction amount per currency.
* `MAX_AMOUNT: Dict[Currency, float]` → Maximum transaction amount per currency.
* `VERSION: str` → Version of the adapter (default `"1.0.0"`).
* `client: Optional[HTTPClient]` → Reusable HTTP client instance.

---

### Constructor

```python
def __init__(self, config: ProviderConfig, context: Optional[Dict[str, Any]] = None)
```

* `config` → Holds provider credentials and environment info (sandbox/production).
* `context` → Optional dict with extra metadata (e.g., debug flags, request ID, etc.).

This constructor is automatically called when you **instantiate** an adapter.

---

### Utility Methods

#### `get_client() -> HTTPClient`

* Ensures an HTTP client is available.
* Reuses the same client for performance.

#### `get_context() -> Dict[str, Any]`

* Returns extra context passed at instantiation.
* Useful for logging, tracing, or debugging.

#### `supports_partial_refund() -> bool`

* Returns `True` if the provider supports **partial refunds**.
* Default: `False`.

#### `provider_name() -> str`

* Returns a **normalized provider name**.
* E.g. `SemoaAdapter` → `"semoa"`.

---

### Abstract Methods (Must Be Implemented)

Every adapter **must implement** the following methods.

| Method                                   | Purpose                                          | Example Use                            |
| ---------------------------------------- | ------------------------------------------------ | -------------------------------------- |
| `get_headers(authorization=False)`       | Build HTTP headers for requests                  | Add `"Authorization: Bearer <token>"`  |
| `get_credentials()`                      | Return provider credentials                      | Used internally to sign requests       |
| `send_payment(transaction)`              | Send a new payment request                       | User pays via Semoa/MTN/Wave           |
| `check_status(transaction_id)`           | Query transaction status                         | Polling until success/failure          |
| `cancel_transaction(transaction_id)`     | Cancel a pending transaction                     | Not all providers support it           |
| `get_transaction_detail(transaction_id)` | Get detailed transaction info                    | Fetch amount, payer, status            |
| `refund(transaction_id, amount, reason)` | Process a refund                                 | Full or partial refund                 |
| `validate_webhook(payload, headers)`     | Verify incoming webhook signature                | Prevent spoofed requests               |
| `parse_webhook(payload, headers)`        | Parse provider webhook → EasySwitch format       | Normalize webhook events               |
| `validate_credentials(credentials)`      | Ensure credentials are valid                     | Check API key correctness              |
| `format_transaction(data)`               | Convert EasySwitch transaction → provider format | For sending requests                   |
| `get_normalize_status(status)`           | Map provider status → standardized status        | `"paid"` → `TransactionStatus.SUCCESS` |

---

### Validation Methods

#### `get_required_fields() -> List[str]`

Returns the required config fields for this adapter.

#### `validate_transaction(transaction: TransactionDetail) -> bool`

Checks if the transaction is valid:

* Amount within min/max range.
* Currency supported.
* Phone number format valid.

Raises exception if invalid.

---

### URL Resolver

#### `_get_base_url() -> str`

Returns the correct base URL depending on the environment:

* Sandbox → `SANDBOX_URL`.
* Production → `PRODUCTION_URL`.

---

## ✅ Example – Implementing a Custom Adapter

```python
from easyswitch.adapters.base import BaseAdapter, AdaptersRegistry
from easyswitch.types import PaymentResponse, TransactionDetail, TransactionStatus

@AdaptersRegistry.register("semoa")
class SemoaAdapter(BaseAdapter):
    SANDBOX_URL = "https://sandbox.semoa.com/api"
    PRODUCTION_URL = "https://api.semoa.com"
    SUPPORTED_CURRENCIES = ["XOF"]

    def get_headers(self, authorization=False):
        return {
            "Authorization": f"Bearer {self.config.api_key}" if authorization else "",
            "Content-Type": "application/json"
        }

    def get_credentials(self):
        return self.config

    async def send_payment(self, transaction: TransactionDetail) -> PaymentResponse:
        # TODO: Call Semoa API
        ...

    async def check_status(self, transaction_id: str) -> TransactionStatus:
        # TODO: Implement status polling
        ...

    async def cancel_transaction(self, transaction_id: str) -> bool:
        return False  # not supported

    async def refund(self, transaction_id: str, amount=None, reason=None) -> PaymentResponse:
        ...

    async def validate_webhook(self, payload, headers) -> bool:
        return True

    async def parse_webhook(self, payload, headers) -> dict:
        return {"status": "parsed"}

    def validate_credentials(self, credentials) -> bool:
        return bool(credentials.api_key)
```

---

## 📝 Developer Checklist for Writing a New Adapter

Before publishing your adapter, make sure you:

* [ ] Define `SANDBOX_URL` and `PRODUCTION_URL`.
* [ ] Set `SUPPORTED_CURRENCIES`.
* [ ] Implement `send_payment()`.
* [ ] Implement `check_status()`.
* [ ] Implement `refund()` (if supported).
* [ ] Handle webhooks: `validate_webhook()` + `parse_webhook()`.
* [ ] Normalize provider-specific statuses with `get_normalize_status()`.
* [ ] Validate credentials in `validate_credentials()`.
* [ ] Add proper headers in `get_headers()`.
