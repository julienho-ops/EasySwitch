# Install EasySwitch

## Requirements

- :material-language-python: Python >=3.9
- :material-package-variant: Package manager (`pip` or `uv` recommanded)
- :material-lock: API credentials for any supported payment provider (PayGate, FedaPay, etc.)

## Install

=== "Using pip (standard)"
    ```bash
    pip install easyswitch
    ```

=== "Using UV (ultra-fast)"
    ```bash
    # First install UV
    pip install uv

    # Then install EasySwitch
    uv pip install easyswitch

    # Or 
    uv add easyswitch
    ```

=== "Install from sources"
    ```bash
    git clone https://github.com/your-repo/easyswitch.git
    cd easyswitch
    pip install -e .[dev]  # Development mode
    ```

## Check installation

```python
import easyswitch
print(easyswitch.__version__)
# Example output: '1.0.0'
```