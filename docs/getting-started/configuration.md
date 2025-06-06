## ⚙️ Configuration
EasySwitch uses a centralized configuration object to provide a flexible, type-safe, and validated configuration system that lets you control the behavior of the SDK: environment setup, payment providers, logging, and more.

### 🔁 Overview

The main configuration object is RootConfig. You can load it from a file, environment variable, or any custom source via a class that extends BaseConfigSource.

---

### 📦 `RootConfig`

The central configuration class. It defines all the required settings to run EasySwitch.

#### Attributes:

| Attribute          | Type                              | Description                                                         |                                                        |
| ------------------ | --------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------ |
| `debug`            | `bool`                            | Enables debug mode (more verbose logging).                          |                                                        |
| `logging`          | [`LoggingConfig`](#loggingconfig) | Logging configuration.                                              |                                                        |
| `default_currency` | `str`                             | Default currency for transactions (must be in the `Currency` enum). |                                                        |
| `providers`        | `Dict[Provider, ProviderConfig]`  | Dictionary of enabled payment providers.                            |                                                        |
| `default_provider` | \`Provider                        | None\`                                                              | Default provider used if none is explicitly specified. |

---

## 🔧 `ProviderConfig`

Represents configuration for **each individual payment provider**.

### Attributes:

| Attribute      | Type             | Description                                 |                                               |
| -------------- | ---------------- | ------------------------------------------- | --------------------------------------------- |
| `api_key`      | \`str            | None\`                                      | Public key or client ID.                      |
| `api_secret`   | \`str            | None\`                                      | Private key or client secret.                 |
| `token`        | \`str            | None\`                                      | Access token (used by some providers).        |
| `base_url`     | \`str            | None\`                                      | API base URL for the provider.                |
| `callback_url` | \`str            | None\`                                      | URL to receive provider notifications.        |
| `return_url`   | \`str            | None\`                                      | URL to redirect after payment.                |
| `timeout`      | `int`            | Maximum duration of a request (in seconds). |                                               |
| `environment`  | \`"sandbox"      | "production"\`                              | Environment in which the provider should run. |
| `extra`        | `Dict[str, Any]` | Additional data specific to the provider.   |                                               |

### Validation:

* Either `api_key` or `api_secret` must be provided.
* `environment` must be either `"sandbox"` or `"production"`.

---

---

## 🧾 `LoggingConfig`

Handles all SDK logging options.

| Attribute  | Type                               | Description                         |                        |
| ---------- | ---------------------------------- | ----------------------------------- | ---------------------- |
| `enabled`  | `bool`                             | Enable or disable logging.          |                        |
| `level`    | `LogLevel` (`debug`, `info`, etc.) | Logging verbosity level.            |                        |
| `file`     | \`str                              | None\`                              | File to write logs to. |
| `console`  | `bool`                             | Enable console output for logs.     |                        |
| `max_size` | `int`                              | Max log file size (in MB).          |                        |
| `backups`  | `int`                              | Number of backup log files to keep. |                        |
| `compress` | `bool`                             | Whether to compress old logs.       |                        |
| `format`   | `LogFormat` (`plain`, `json`)      | Log output format.                  |                        |
| `rotate`   | `bool`                             | Enable automatic log file rotation. |                        |

---

## 🔒 Built-in Validation

The SDK uses [Pydantic](https://docs.pydantic.dev) to ensure strict validation of all configuration fields. If something is misconfigured, a `ConfigurationError` is raised.

### Validation Examples:

```python
# Invalid currency
default_currency = "USD"  # Error: USD is not defined in Currency enum

# Invalid default provider
default_provider = "STRIPE"  # Error if STRIPE is not present in the `providers` dictionary
```

---

### **1. ⚙️ Supported Configuration sources**  

| Source               | Description                                  | Example |
|-----------------------|---------------------------------------------|---------|
| **Environment Variables**   | Load configs from a `.env` file or System Environment | [see example](#-exemple-de-fichier-env) |
| **Native Python Dictionary** | Direct configuration in your code          | [see exemple](#-configuration-depuis-un-dictionnaire) |
| **JSON File**      | Load configs from a JSON file           | [see example](#-configuration-depuis-json) |
| **YAML File**      | Load configs from a YAML file           | [see example](#-configuration-depuis-yaml) |




### **🔹 Example of `.env` file**

```ini
# This file is a sample. Copy it to .env and fill in the values.

# General configuration
EASYSWITCH_ENVIRONMENT=sandbox                  # or production
EASYSWITCH_TIMEOUT=30                           # seconds
EASYSWITCH_DEBUG=true                           # Enable debug mode

# Logging configuration
# Note: Logging configuration is only used if EASYSWITCH_LOGGING is set to true

EASYSWITCH_LOGGING=true                         # Enable file logging
EASYSWITCH_LOG_LEVEL=info                       # debug, info, warning, error
EASYSWITCH_LOG_FILE=/var/log/easyswitch.log     # Path to the log file
EASYSWITCH_CONSOLE_LOGGING=true                 # Enable console logging
EASYSWITCH_LOG_MAX_SIZE=10                      # Maximum size of the log file in MB
EASYSWITCH_LOG_BACKUPS=5                        # Number of backup log files to keep
EASYSWITCH_LOG_COMPRESS=true                    # Whether to compress old log files
EASYSWITCH_LOG_FORMAT=plain                     # Format of the log file (plain or json)
EASYSWITCH_LOG_ROTATE=true                      # Whether to rotate the log file

# Payment gateway configuration
EASYSWITCH_ENABLED_PROVIDERS=cinetpay,semoa     # Comma-separated list of enabled payment providers
EASYSWITCH_DEFAULT_PROVIDER=cinetpay            # Default payment provider
EASYSWITCH_CURRENCY=XOF                         # Default currency

# Providers configuration
# NOTE: these are standadized variables for all providers. 

# CINETPAY
# Note: Only required if EASYSWITCH_ENABLED_PROVIDERS includes 'cinetpay'
# You don't need to fill in all of these variables. Only fill in the ones you need.
EASYSWITCH_CINETPAY_API_KEY=your_cinetpay_api_key
EASYSWITCH_CINETPAY_X_SECRET=your_cinetpay_secret_key
EASYSWITCH_CINETPAY_X_STIE_ID=your_cinetpay_site_id
EASYSWITCH_CINETPAY_CALLBACK_URL=your_cinetpay_callback_url
EASYSWITCH_CINETPAY_X_CHANNELS=ALL
EASYSWITCH_CINETPAY_X_LANG=fr

# SEMOA
# Note: Only required if EASYSWITCH_ENABLED_PROVIDERS includes 'semoa'
# You don't need to fill in all of these variables. Only fill in the ones you need.
EASYSWITCH_SEMOA_API_KEY=your_semoa_api_key
EASYSWITCH_SEMOA_X_CLIENT_ID=your_semoa_client_id
EASYSWITCH_SEMOA_X_CLIENT_SECRET=your_semoa_client_secret
EASYSWITCH_SEMOA_X_USERNAME=your_semoa_username
EASYSWITCH_SEMOA_X_PASSWORD=your_semoa_password
EASYSWITCH_SEMOA_X_CALLBACK_URL=your_semoa_callback_url   # Optional
```

---

### **🔹 Example of python dictionary** 

```python
from easyswitch import (
    EasySwitch, TransactionDetail, Provider,
    TransactionStatus, Currency, TransactionType,
    CustomerInfo
)

config = {
    "debug": True,
    "providers": {
        Provider.CINETPAY: {
            "api_key": "your_api_key",
            "base_url": "https://api.exemple.com/v1", # Optional
            "callback_url": "https://api.exemple.com/v1/callback",
            "return_url": "https://api.exemple.com/v1/return",
            "environment": "production",     # Optional sandbox by default
            "extra": {
                "secret": "your_secret",
                "site_id": "your_site_id",
                "channels": "ALL",     # More details on Cinetpay's documentation.
                "lang": "fr"        # More details on Cinetpay's documentation.
            }
        },
        Provider.BIZAO: {
            "api_key": "your_api_key",
            "base_url": "https://api.exemple.com/v1", # Optional
            "callback_url": "https://api.exemple.com/v1/callback",
            "return_url": "https://api.exemple.com/v1/return",
            "environment": "production",     # Optional sandbox by default
            "timeout":30,
            "extra": {
                # Dev Configs
                "dev_client_id": "your_dev_client_id",
                "dev_client_secret": "your_dev_client_secret",
                "dev_token_url": "https://your_dev_token_url.com",     

                # Prod Configs
                "prod_client_id": "your_prod_client_id",
                "prod_client_secret": "your_prod_client_secret",
                "prod_token_url": "https://your_dev_token_url.com",

                # Global configs
                "country-code": Countries.IVORY_COAST,
                "mno-name": "orange",
                "channel": "web",
                "lang": "fr",
                "cancel_url": "https/example.com/cancel"
            }
        },
    }
}

client = EasySwitch.from_dict(config)
```

---

### **🔹 Configuration from JSON file**  

```json
// config.json
{
  "debug": true,
  "default_currency": "XOF",
  "default_provider": "CINETPAY",
  "logging": {
    "enabled": true,
    "level": "info",
    "file": "logs/easyswitch.log",
    "console": true,
    "rotate": true,
    "compress": true,
    "format": "plain"
  },
  "providers": {
    "CINETPAY": {
      "api_key": "your_cinetpay_api_key",
      "base_url": "https://sandbox.example.com/api",
      "callback_url": "https://example.com/callback",
      "environment": "sandbox",
      "extra": {
        "secret": "your_cinetpay_secret_key",
        "site_id": "your_cinetpay_site_id",
        "channels": "ALL",
        "lang": "fr"
      }
    },
    "SEMOA": {
      "api_key": "your_semoa_api_key",
      "base_url": "https://api.stripe.com",
      "environment": "production",
      "extra": {
        "client_id": "your_semoa_client_id",
        "client_secret": "your_semoa_client_secret",
        "username": "your_semoa_username",
        "password": "your_semoa_password"
      }
    }
  }
}
```

```python
client = EasySwitch.from_json("config.json")
```

---

### **🔹 Configuration from YAML file**  

```yaml
debug: true
default_currency: XOF
default_provider: CINETPAY

logging:
    enabled: true
    level: info
    file: logs/easyswitch.log
    console: true
    rotate: true
    compress: true
    format: plain

# Configure Providers
providers:
    # CinetPay Configs
    CINETPAY:
        api_key: your_cinetpay_api_key
        base_url: https://sandbox.example.com/api
        callback_url: https://example.com/callback
        environment: sandbox
        extra:
            secret: your_cinetpay_secret_key
            site_id: your_cinetpay_site_id
            channels: ALL
            lang: fr

    # Semoa Configs
    SEMOA:
        api_key: your_semoa_api_key
        base_url: https://api.stripe.com
        environment: production
        extra:
            client_id: your_semoa_client_id
            client_secret: your_semoa_client_secret
            username: your_semoa_username
            password: your_semoa_password
        
```

```python
client = EasySwitch.from_yaml("config.yaml")
```

---

##  Creating new configuration source

### 🔌 `BaseConfigSource`

Abstract base class used to implement custom configuration sources, such as files, environment variables, remote services, etc.

```python
from easyswitch.conf import register_source

# Use @register_source decorator to regiter 
# your config source loader class
@register_source('toml')
class MyTomlConfigSource(BaseConfigSource):
    def __init__(self, path: str):
        self.path = path

    def is_valid(self) -> bool:
        return Path(self.path).exists()

    def load(self) -> Dict[str, Any]:
        with open(self.path, 'r') as f:
            return toml.safe_load(f)
```

---

## 🧪 Usage Example

```python
from easyswitch.conf import CommandManager
from my_source import MyTomlConfigSource
from easyswitch import EasySwwitch

# Create config manager using MyTomlConfigSource tag 'toml'
manager = CommandManager.add_source(
    'toml',                 # Which references MyTomlConfigSource class
    path = "config.toml"    # .toml file path
).load()

# Use it to configure client
client = EasySwitch(config = manager.get_config())
...
```

---

## ✅ Summary

The EasySwitch configuration system is:

* ✅ Strongly typed
* ✅ Automatically validated
* ✅ Flexible and extensible
* ✅ Safe and secure

It gives you full control over how payment providers are integrated and managed in your applications.

For more details on how to use the `RootConfig` object with other parts of the SDK, check the [API Reference](../api-reference.md).