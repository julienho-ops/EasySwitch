# EasySwitch😎 Python Library

**EasySwitch** is a unified **Python SDK for Mobile Money** integration across major aggregators in West Africa. It provides a single, consistent interface to simplify payment processing, reduce code duplication, and accelerate development.

## Currently Supported Providers
- <img src = 'https://cinetpay.com/brand/logo-cinetpay.webp' height = 60 ></img>
- <img src = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9eIXxPvwTKAgJYxFO7mR6ZGIrTaK16qFI0UsGnIQg&s' height = 60 ></img>
- <img src = 'https://www.fedapay.com/wp-content/themes/fedapay_theme/pictures/feda-logo-blue-new.svg' height = 60 ></img> 

## Next
We will add progressively support for following Providers:
- <img src = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT3sWIPK8p28IQhWbqKpewYYtCHZaAk6O98T4dUiEhp&s' height = 60 ></img> 
<span style = 'margin-left:10'></span>
<img src = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQstE0NII74XhnGdDhMDWpA-7uL55uaooz3fn-yjrvl6g&s' height = 60 ></img><span style = 'margin-left:10'></span><img src = 'https://asset.brandfetch.io/idBsplB3mt/idyp_5HZE4.png' height = 55 >
</img>

- <img src = 'https://bankassurafrik.com/wp-content/uploads/2022/07/telechargement-2.png' height = 60 ></img>
<span style = 'margin-left:10'></span><img src = 'https://payplus.africa/img/logo.png' height = 60 ></img>
<span style = 'margin-left:10'></span>
<img src = 'https://paydunya.com/refont/images/logo/blue_logo.png' height = 60 ></img>



## Prerequisites

You need to have at least 3.9 version of python to be able to continue. To do this:


Next you can go ahead with `iSwitch`.

## Install

```sh
pip install iswitch
```

## API

The iSwitch Python library's API is designed around the [SWITCHPAY REST API](https://github.com/AllDotPy/SwitchPay)

### Settings
```python
from iswitch import Client

# Creating a client
client = Client(
    configs = {
        'host':'',                          # Your API Host or localhost:9000 by Default
        'service': 'SEMOA',                 # The Provider Service to use
        'raise_on_error': False,            # If True, client will raise on request errors
        'credentials':{
            'username':'YOUR-APP-USERNAME',
            'password':'YOUR-APP-PASSWORD',
        }
    }
)
```

### Authentication
```python
response = client.authenticate()

if not response.has_error:
    print(type(response))      # <class 'iswitch._types.Response'>
    data = response.json
    ...
else :
    print(type(response))      # <class 'iswitch._types.ErrorResponse'>
```

### Get active application
```python
app = client.get_application()
```

## Providres

### Get Provider
```python
provider = client.get_provider()
```

### List Providers

```python
response = client.list_providers()
```

## Transactions 

### Create Order
```python
# Creating order for SEMOA Transaction.
semoa_order = {
    'merchant_reference': '13fx5er5v7',
    'client': {
        'last_name': 'Doe',
        'first_name': 'John',
        'phone': '+123456789',
    }
}

# Creating order for CINETPAY Transaction.
cinetpay_order = {
    'transaction_id': '123456',
    'currency': 'XOF',
    'description': 'YOUR-ORDER-DESCRIPTION',
    'customer_name': 'Doe',
    'customer_surname': 'John',
}
```

### Create Transaction

```python
from iSwitch import Client, Transaction

# Initializing Client
client = Client(
    configs = {
        'host':'',
        'service': 'CINETPAY',
        'raise_on_error': False,
        'credentials':{
            'username':'YOUR-APP-USERNAME',
            'password':'WRONG-PASSWORD',
        }
    }
)

# Creating Transaction
transaction = Transaction(
    amount = 250,
    callback_url = 'YOUR-CALLBACK-URL',
    return_url='YOUR-RETURN/REDIRECT-URL',
    order = cinetpay_order
)

response = client.create_transaction(transaction)
print(type(response))       # <Class Response status: 201 error: False>

```

### List Transactions
To list transactions you can use `list_transactions` function.
```python
response = client.list_transactions()
```

### Retrieve Transaction
To get a specific transaction you can use the `get_transaction` function.
```python
response = client.get_transaction(transaction_id)
```

### Get a Specific Transaction payment url
You can also get a payment URL for a specific Transaction using `get_bill_url` function.
```python
response = client.get_bill_url(transaction_id)
```

## Responses
- ### Response class
The default Request response class, is returned when `detail` is set to `True` in the request.
```python
response = client.create_transaction(my_transaction)

print(response)         # <Class Response status: 201, error: False>

# Use json attribute to access response data.
print(response.json)   # {"id":transaction_id,...}
```
- ### PagginatedResponse Class
PagginatedResponse is used to manage Pagginated response data. It provides properties such as :
- `has_next` : bool , `True` if the PagginatedResponse has a next page else `False`.
- `has_prev` : bool, `True` if the PagginatedResponse has a next page else `False`
- `next_page` : PagginatedResponse, the next page if `has_next` is `True`
- `previous_page` : PagginatedResponse, the next page if `has_prev` is `True`
- `result` : sequence[ Mapping[ str,any ] ], the page data.

## Errors

Errors are raised if requests return an error status.

- ### ErrorResponse class

This Error is returned if raise_on_error is set to True in Client configs.

```python
from iSwitch import Client

client = Client(
    configs = {
        'host':'',
        'service': 'SEMOA',
        'raise_on_error': False,
        'credentials':{
            'username':'YOUR-APP-USERNAME',
            'password':'WRONG-PASSWORD',
        }
    }
)

# Do Authentication
response = Client.authenticate()

# With raise_on_error set to False
print(type(response))           # <class 'iswitch._types.ErrorResponse'>
print(response.get_message())   # Invalid password.
```

- ### ResponseError class
This Error is raised if raise_on_error is set to True in Client configs.

```python
from iSwitch import Client

client = Client(
    configs = {
        'host':'',
        'service': 'SEMOA',
        'raise_on_error': True,
        'credentials':{
            'username':'YOUR-APP-USERNAME',
            'password':'WRONG-PASSWORD',
        }
    }
)

# Do Authentication
response = Client.authenticate()        # Will raise a ResponseError with response message.
```
<br>
<p align = 'center'>
    <img src='dotpy_blue_transparent.png?raw=true' height = '60'></img>
</p>
<p align = 'center'>Made with ❤️ By DotPy</p>
<!-- <p height='60' align = 'center'>© 2024 DotPy, Inc. All rights reserved.</p> -->
