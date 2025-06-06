# :material-home: EasySwitch Documentation

<div class="grid cards" markdown>

-   :material-power:{ .lg .middle } __Get Started__

    ---

    Set up **EasySwitch** and make your first API call in minutes.

    [-> Installation Guide](getting-started/installation.md)

-   :material-api:{ .lg .middle } __API Reference__

    ---

    Complete reference for all available methods and configurations.

    [-> API Documentation](api-reference.md)

-   :material-cellphone-arrow-down:{ .lg .middle } __Payment Guides__

    ---

    Learn how to process mobile money payments across different providers.

    [-> Send Payments](guides/payments.md) | [-> Webhooks](guides/webhooks.md)

-   :material-github:{ .lg .middle } __Contribute__

    ---

    Help improve EasySwitch with your contributions and feedback.

    [-> Contribution Guide](contributing.md)

</div>

## :material-head-question-outline: What is EasySwitch?

EasySwitch is a unified Python SDK for integrating mobile money APIs across West Africa. It standardizes multiple payment providers behind a single interface while maintaining flexibility and security.

Key features:

- **Unified API** for Bizao, PayGate, FedaPay, CinetPay, and more
- **Async-first** design for high performance
- **Multi-source configuration** (JSON, YAML, environment variables)
- **Enterprise-grade security** with webhook validation

Explore further:

- [GitHub Repository](https://github.com/your-repo/easyswitch) for source code and issues
- [PyPI Package](https://pypi.org/project/easyswitch/) for latest releases
- [Community Forum](#) (coming soon) for support and discussions

## :material-lightning-bolt: Quick Example

```python
from easyswitch import (
    EasySwitch, TransactionDetail, Provider,
    TransactionStatus, Currency, TransactionType,
    CustomerInfo
)

# Initialize client
client = EasySwitch.from_env()


# Creating a Transaction
order = TransactionDetail(
    transaction_id = 'xveahdk-82998n9f8uhgj',
    provider = Provider.CINETPAY,
    status = TransactionStatus.PENDING, # Default value
    currency = Currency.XOF,
    amount = 150,
    transaction_type = TransactionType.PAYMENT,  # Default value
    reason = 'My First Transaction Test with EasySwitch\'s CinetPay client.',
    reference = 'my_ref',
    customer = CustomerInfo(
        phone_number = '+22890000000',
        first_name = 'Wil',
        last_name = 'Eins',
        address = '123 Rue képui, Lomé', # Optional
        city = 'Lomé',  # Optional
    )
)

# Send mobile money payment
response = client.send_payment(
    order
)

print(f"Payment initiated!")
```