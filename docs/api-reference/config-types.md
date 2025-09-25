# Configuration Models (`easyswitch.conf.base`)

This module defines the **configuration system** for EasySwitch.
It provides base classes, validation logic, and standardized structures to configure providers, logging, and root settings.

---

## 🔹 Enumerations

### `LogLevel`

Defines the available **logging levels**.

| Value      | Description                       |
| ---------- | --------------------------------- |
| `debug`    | Detailed debugging logs.          |
| `info`     | General information logs.         |
| `warning`  | Warnings that may need attention. |
| `error`    | Errors that occurred.             |
| `critical` | Critical errors, system failures. |

---

### `LogFormat`

Defines the available **logging output formats**.

| Value   | Description                     |
| ------- | ------------------------------- |
| `plain` | Standard human-readable logs.   |
| `json`  | Structured logs in JSON format. |

---

## 🔹 Models

### `LoggingConfig`

Configuration model for **application logging**.

```python
class LoggingConfig(BaseModel):
    enabled: bool = False
    level: LogLevel = LogLevel.INFO
    file: Optional[str] = None
    console: bool = True
    max_size: int = 10  # MB
    backups: int = 5
    compress: bool = True
    format: LogFormat = LogFormat.PLAIN
    rotate: bool = True
```

**Fields:**

* `enabled` – Enable/disable logging (`False` by default).
* `level` – Log level (`LogLevel` enum).
* `file` – File path for logs (if any).
* `console` – Print logs to console.
* `max_size` – Maximum file size before rotation (MB).
* `backups` – Number of backup log files to keep.
* `compress` – Whether to compress rotated logs.
* `format` – Log format (`plain` or `json`).
* `rotate` – Enable log rotation.

---

### `BaseConfigModel`

A **base class** for all configuration models.
Provides extra validation rules via Pydantic.

* Forbids extra/undefined fields.
* Enforces enum values.
* Validates all fields strictly.

---

### `ProviderConfig`

Defines configuration for a **payment provider**.

```python
class ProviderConfig(BaseConfigModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    token: Optional[str] = None
    base_url: Optional[str] = None
    callback_url: Optional[str] = None
    return_url: Optional[str] = None
    timeout: int = 30
    environment: str = "sandbox"   # "sandbox" | "production"
    extra: Dict[str, Any] = {}
```

**Validations:**

* `environment` must be `"sandbox"` or `"production"`.
* At least one of `api_key` or `api_secret` must be provided.

**Fields:**

* `api_key`, `api_secret`, `token` – Authentication credentials.
* `base_url` – Provider API base URL.
* `callback_url` – Callback URL for webhooks.
* `return_url` – URL to redirect users after a transaction.
* `timeout` – API request timeout (seconds).
* `environment` – `"sandbox"` or `"production"`.
* `extra` – Extra provider-specific settings.

---

### `RootConfig`

The **root configuration** for EasySwitch.

```python
class RootConfig(BaseConfigModel):
    debug: bool = False
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    default_currency: str = Currency.XOF
    providers: Dict[Provider, ProviderConfig] = Field(default_factory=dict)
    default_provider: Optional[Provider] = None
```

**Fields:**

* `debug` – Enable debug mode if `True`.
* `logging` – Logging configuration (`LoggingConfig`).
* `default_currency` – Default currency (`Currency` enum).
* `providers` – Dictionary of enabled providers (`ProviderConfig` per provider).
* `default_provider` – Default provider (must exist in `providers`).

**Validations:**

* `default_provider` must be:

  * Included in the enabled `providers`.
  * A valid supported provider (`Provider` enum).
* `default_currency` must be a valid value in `Currency`.

---

### `BaseConfigSource`

An abstract base class (interface) for **configuration sources**.
Any custom configuration loader (e.g., from environment, file, database) must implement it.

```python
class BaseConfigSource(ABC):
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load configurations from the source."""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if the source is valid."""
        pass
```

---

## ✅ Example Usage

```python
from easyswitch.conf.base import RootConfig, ProviderConfig, LoggingConfig, LogLevel, LogFormat
from easyswitch.types import Provider, Currency

config = RootConfig(
    debug=True,
    logging=LoggingConfig(
        enabled=True,
        level=LogLevel.DEBUG,
        format=LogFormat.JSON
    ),
    default_currency=Currency.XOF,
    providers={
        Provider.SEMOA: ProviderConfig(
            api_key="your-api-key",
            api_secret="your-api-secret",
            environment="sandbox"
        )
    },
    default_provider=Provider.SEMOA
)
```
