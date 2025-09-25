# 📖 Shared Types

The `easyswitch.types` module defines **shared enums, dataclasses, and structures** used across the EasySwitch SDK.
These ensure that all providers, responses, and events follow a consistent format.

---

## 🏦 Providers

```python
class Provider(str, Enum)
```

Represents the list of **supported payment aggregators**.

| Member     | Value        | Description          |
| ---------- | ------------ | -------------------- |
| `SEMOA`    | `"SEMOA"`    | Semoa aggregator.    |
| `BIZAO`    | `"BIZAO"`    | Bizao aggregator.    |
| `CINETPAY` | `"CINETPAY"` | CinetPay aggregator. |
| `PAYGATE`  | `"PAYGATE"`  | PayGate aggregator.  |
| `FEDAPAY`  | `"FEDAPAY"`  | FedaPay aggregator.  |

✅ Used whenever you need to specify or identify the payment provider.

---

## 💱 Currency

```python
class Currency(str, Enum)
```

Represents the **supported currencies**.

| Member | Value   | Description                      |
| ------ | ------- | -------------------------------- |
| `XOF`  | `"XOF"` | CFA Franc BCEAO (West Africa).   |
| `XAF`  | `"XAF"` | CFA Franc BEAC (Central Africa). |
| `NGN`  | `"NGN"` | Nigerian Naira.                  |
| `GHS`  | `"GHS"` | Ghanaian Cedi.                   |
| `EUR`  | `"EUR"` | Euro.                            |
| `USD`  | `"USD"` | US Dollar.                       |
| `CDF`  | `"CDF"` | Congolese Franc.                 |
| `GNF`  | `"GNF"` | Guinean Franc.                   |
| `KMF`  | `"KMF"` | Comorian Franc.                  |

---

## 🌍 Countries

```python
class Countries(str, Enum)
```

Represents the **supported countries**.

| Member        | Value  | Description   |
| ------------- | ------ | ------------- |
| `TOGO`        | `"TG"` | Togo          |
| `BENIN`       | `"BJ"` | Benin         |
| `GHANA`       | `"GH"` | Ghana         |
| `BURKINA`     | `"BF"` | Burkina Faso  |
| `IVORY_COAST` | `"CI"` | Côte d’Ivoire |

---

## 🔄 Transaction Types

```python
class TransactionType(str, Enum)
```

Represents the **operation type** of a transaction.

| Member       | Value          | Description                             |
| ------------ | -------------- | --------------------------------------- |
| `PAYMENT`    | `"payment"`    | Standard payment (customer → merchant). |
| `DEPOSIT`    | `"deposit"`    | Deposit into a wallet/account.          |
| `WITHDRAWAL` | `"withdrawal"` | Withdraw from a wallet/account.         |
| `REFUND`     | `"refund"`     | Refund of a previous transaction.       |
| `TRANSFER`   | `"transfer"`   | Transfer between accounts.              |

---

## 📊 Transaction Status

```python
class TransactionStatus(str, Enum)
```

Possible **states** of a transaction.

| Member        | Value           | Meaning                             |
| ------------- | --------------- | ----------------------------------- |
| `PENDING`     | `"pending"`     | Waiting to be processed.            |
| `SUCCESSFUL`  | `"successful"`  | Completed successfully.             |
| `FAILED`      | `"failed"`      | Failed permanently.                 |
| `ERROR`       | `"error"`       | Technical error.                    |
| `CANCELLED`   | `"cancelled"`   | Cancelled by user/system.           |
| `REFUSED`     | `"refused"`     | Refused by provider.                |
| `DECLINED`    | `"declined"`    | Declined (e.g. insufficient funds). |
| `EXPIRED`     | `"expired"`     | Payment expired.                    |
| `REFUNDED`    | `"refunded"`    | Transaction refunded.               |
| `PROCESSING`  | `"processing"`  | In progress.                        |
| `INITIATED`   | `"initiated"`   | Initiated but not yet processed.    |
| `UNKNOWN`     | `"unknown"`     | Unknown state.                      |
| `COMPLETED`   | `"completed"`   | Fully completed.                    |
| `TRANSFERRED` | `"transferred"` | Successfully transferred.           |

---

## 📦 Data Structures

### 🔎 `TransactionStatusResponse`

```python
@dataclass
class TransactionStatusResponse:
    transaction_id: str
    provider: Provider
    status: TransactionStatus
    amount: float
    data: Dict[str, Any]
```

Represents a **standardized status response** from a provider.

---

### 👤 `CustomerInfo`

```python
@dataclass
class CustomerInfo:
    phone_number: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    ...
```

Represents **customer details** attached to a transaction.

Useful for receipts, fraud detection, and refunds.

---

### 💳 `PaymentResponse`

```python
@dataclass
class PaymentResponse:
    transaction_id: str
    provider: Provider
    status: TransactionStatus
    amount: float
    currency: Currency
    ...
```

Standardized structure returned after a payment request.

#### Properties:

* `is_successful` → `True` if status is `SUCCESSFUL`
* `is_pending` → `True` if status is `PENDING`, `PROCESSING`, or `INITIATED`
* `is_failed` → `True` if status is `FAILED`, `CANCELLED`, or `EXPIRED`

---

### 📑 `TransactionDetail`

```python
@dataclass
class TransactionDetail:
    transaction_id: str
    provider: Provider
    amount: float
    currency: Currency
    status: TransactionStatus
    transaction_type: TransactionType
    ...
```

Represents a **complete record** of a transaction, including metadata, customer info, and timestamps.

---

### 📡 `WebhookEvent`

```python
@dataclass
class WebhookEvent:
    event_type: str
    provider: Provider
    transaction_id: str
    status: TransactionStatus
    amount: float
    currency: Currency
    ...
```

Represents a standardized **webhook notification event**.

---

### 🔑 `ApiCredentials`

```python
@dataclass
class ApiCredentials:
    api_key: str
    api_secret: Optional[str]
    client_id: Optional[str]
    ...
```

Represents authentication credentials for a provider.

#### Utility methods:

* `load_from_env(provider: Provider)` → Loads credentials from environment variables prefixed with `EASYSWITCH_<PROVIDER>_`.
* `write_to_env(provider: Provider)` → Saves credentials to environment variables.

✅ Example:

```bash
export EASYSWITCH_CINETPAY_API_KEY="pk_test_123"
export EASYSWITCH_CINETPAY_API_SECRET="sk_test_123"
```

```python
creds = ApiCredentials(api_key="")
creds.load_from_env(Provider.CINETPAY)
print(creds.api_key)  # => pk_test_123
```

---

### 📖 `PaginationMeta`

```python
@dataclass
class PaginationMeta:
    current_page: int
    next_page: Optional[int]
    prev_page: Optional[int]
    per_page: int
    total_pages: int
    total_count: int
```

Standardized structure used when listing or paginating transactions.

---

## ✅ Summary

The `easyswitch.types` module provides:

* Unified enums for **providers, currencies, statuses, and transaction types**.
* Standardized dataclasses for **transactions, customers, payments, webhooks, and pagination**.
* A common **API credentials system** with built-in env helpers.

These types ensure all providers work seamlessly and consistently under the EasySwitch SDK.
