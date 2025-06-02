"""
EasySwitch - Shared Types and Data Structures.
"""
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from dateutil import parser

from easyswitch.utils import parse_phone
from easyswitch.utils.currency import FedapayCurrencyMapper


####
##      AVAILABLE PROVIDER CHOICES
#####
class Provider(str, Enum):
    """ Available choices for supported Payment providers. """

    SEMOA = 'SEMOA'
    BIZAO = 'BIZAO'
    CINETPAY = 'CINETPAY'
    PAYGATE = 'PAYGATE'
    FEDAPAY = 'FEDAPAY'


####
##      SUPPORTED CURRENCIES
#####
class Currency(str, Enum):
    """Available Currencies Choices."""

    XOF = "XOF"  # Franc CFA (BCEAO)
    XAF = "XAF"  # Franc CFA (BEAC)
    NGN = "NGN"  # Naira nigérian
    GHS = "GHS"  # Cedi ghanéen
    EUR = "EUR"  # Euro
    USD = "USD"  # Dollar américain
    CDF = "CDF"  # Franc congolais
    GNF = "GNF"  # Franc guinéen
    KMF = "KMF"  # Franc comorien


####
##      SUPPORTED COUNTRIES
#####
class Countries(str, Enum):
    """Supported Countries Choices."""

    TOGO = 'TG'
    BENIN = 'BJ'
    GHANA = 'GH'
    BURKINA = 'BF'
    IVORY_COAST = 'CI'


####
##      TRANSACTION TYPES
#####
class TransactionType(str, Enum):
    """Types de transaction supportés."""

    PAYMENT = "payment"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"
    TRANSFER = "transfer"


####
##      TRANSACTION STATUS
#####
class TransactionStatus(str, Enum):
    """Possible statues of a transaction."""

    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"
    REFUSED = "refused"
    DECLINED = "declined"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    PROCESSING = "processing"
    INITIATED = "initiated"
    UNKNOWN = "unknown"
    COMPLETED = "completed"
    TRANSFERRED = "transferred"


####
##      TRANSACTION STATUS RESPONSE
#####
@dataclass
class TransactionStatusResponse:
    """Standardized Transaction status response structure."""

    transaction_id: str
    provider: Provider
    status: TransactionStatus
    amount: float
    data: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


####
##      CUSTOMER INFORMATION
#####
@dataclass
class CustomerInfo:
    """Customer informations."""

    phone_number: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    zip_code: Optional[str] = None
    state: Optional[str] = None
    id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


####
##      PAYMENT RESPONSE
#####
@dataclass
class PaymentResponse:
    """Standardized Payment response structure."""

    transaction_id: str
    provider: Provider
    status: TransactionStatus
    amount: float
    currency: Currency
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    reference: Optional[str] = None
    payment_link: Optional[str] = None
    transaction_token: Optional[str] = None
    customer: Optional[CustomerInfo] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_successful(self) -> bool:
        """Check if the transaction was successful."""
        return self.status == TransactionStatus.SUCCESSFUL
    
    @property
    def is_pending(self) -> bool:
        """Check if the transaction is pending."""
        return self.status in [
            TransactionStatus.PENDING,
            TransactionStatus.PROCESSING,
            TransactionStatus.INITIATED
        ]
    
    @property
    def is_failed(self) -> bool:
        """Check if the transaction failed."""
        return self.status in [
            TransactionStatus.FAILED,
            TransactionStatus.CANCELLED,
            TransactionStatus.EXPIRED
        ]


####
##      TRANSACTION DETAIL
#####
@dataclass
class TransactionDetail:
    """Standardized Transaction detail structure."""

    transaction_id: str
    provider: Provider
    amount: float
    currency: Currency
    status: TransactionStatus = TransactionStatus.PENDING
    transaction_type: TransactionType = TransactionType.PAYMENT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    customer: Optional[CustomerInfo] = None
    reference: Optional[str] = None
    reason: Optional[str] = None
    callback_url: Optional[str] = None
    return_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def from_fedapay_api(
        data: Dict[str, Any], 
        customer: Optional[CustomerInfo] = None,
        raw_response: Optional[Dict[str, Any]] = None
    ) -> "TransactionDetail":
        return TransactionDetail(
            transaction_id=data.get("id"),
            provider=Provider.FEDAPAY,
            amount=data.get("amount"),
            currency=FedapayCurrencyMapper.get_iso(data.get("currency_id")),
            status=TransactionStatus(data.get("status", "pending")),
            transaction_type=TransactionType.PAYMENT,
            created_at=parser.parse(data.get("created_at")) if data.get("created_at") else None,
            updated_at=parser.parse(data.get("updated_at")) if data.get("updated_at") else None,
            completed_at=parser.parse(data.get("approved_at")) if data.get("approved_at") else None,
            customer=customer or CustomerInfo(id=data.get("customer_id")),
            reference=data.get("reference"),
            reason=data.get("description"),
            callback_url=data.get("callback_url"),
            metadata={k: v for k, v in data.items() if k not in {
                "id", 
                "amount", 
                "currency", 
                "status", 
                "created_at", 
                "updated_at",
                "approved_at",
                "customer_id", 
                "reference", 
                "reason",
                "callback_url",
            }},
            raw_data=raw_response if raw_response is not None else data
        )


####
##      FEDAPAY TRANSACTION UPDATE DETAIL
#####
@dataclass
class FedapayTransactionUpdate:
    """ Standardized FedaPay's transaction update structure. """
    amount: Optional[float] = None
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


####
##      FEDAPAY CUSTOMER UPDATE DETAIL
#####
@dataclass
class FedapayCustomerUpdate:
    """Standardized FedaPay's customer update structure."""
    firstname: str
    lastname: str
    email: Optional[str] = None
    phone_number: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        """Prépare le payload pour l'API FedaPay en ne gardant que les champs renseignés."""
        payload = {}
        
        payload["firstname"] = self.firstname
        payload["lastname"] = self.lastname
        
        if self.email is not None:
            payload["email"] = self.email
        
        # Parse the phone number using the utility function
        parsed_phone = parse_phone(
            self.phone_number,
            raise_exception=True
        )
        
        payload["phone_number"] = {
            "number": parsed_phone.get("national_number"),
            "country": parsed_phone.get("country_alpha2")
        } if parsed_phone else {}
        
        return payload


####
##      WEBHOOK EVENT
#####
@dataclass
class WebhookEvent:
    """Standardized webhook event structure."""

    event_type: str
    provider: Provider
    transaction_id: str
    status: TransactionStatus
    amount: float
    currency: Currency
    created_at: Optional[datetime] = None
    raw_data: Dict[str, Any] = field(default_factory = dict)
    metadata: Dict[str, Any] = field(default_factory = dict)
    context: Dict[str,Any] = field(default_factory = dict)

    # def get_status


####
##      API CREDENTIALS
#####
@dataclass
class ApiCredentials:
    """Authentication credentials for the API."""

    api_key: str
    api_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    merchant_id: Optional[str] = None
    token: Optional[str] = None
    master_key: Optional[str] = None
    private_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[str] = None
    callback_url: Optional[str] = None
    return_url: Optional[str] = None
    channels: Optional[str] = 'MOBILE_MONEY'  # Default to ALL channels
    lang: Optional[str] = 'fr'

    def load_from_env(self,provider: Provider):
        """Load credentials from environment variables."""

        for field in self.__dataclass_fields__:
            env_value = os.getenv(f'EASYSWITCH_{provider.upper()}_{field.upper()}')
            if env_value:
                setattr(self, field, env_value)
        return self
    
    def write_to_env(self,provider: Provider):
        """Write credentials to environment variables."""

        for field in self.__dataclass_fields__:
            env_value = getattr(self, field)
            if env_value:
                os.environ[f'EASYSWITCH_{provider.upper()}_{field.upper()}'] = env_value
        return self


####
##      CURRENCY RESPONSE
#####
@dataclass
class CurrencyResponse:
    """Standardized Currency response structure."""

    currency_id: str
    name: str
    provider: Provider
    iso: Currency
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    modes: List[str] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure modes are unique and always a list."""
        if not isinstance(self.modes, list):
            self.modes = list(self.modes) if self.modes is not None else []
        self.modes = list(set(self.modes))
    

####
##      PAGINATION META
#####
@dataclass
class PaginationMeta:
    current_page: int
    next_page: Optional[int]
    prev_page: Optional[int]
    per_page: int
    total_pages: int
    total_count: int


####
##      CUSTOMER SEARCH RESPONSE
#####
@dataclass
class CustomerSearchResponse:
    customers: List[CustomerInfo]
    meta: PaginationMeta


####
##      TRANSACTION SEARCH RESPONSE
#####
@dataclass
class TransactionSearchResponse:
    transactions: List[TransactionDetail]
    meta: PaginationMeta


#####
##      PAYMENT LINK RESPONSE
#####
@dataclass
class PaymentLinkResponse:
    """ Standardized Payment Link response structure."""
    token: str
    url: str
    raw_response: Optional[Dict[str, Any]] = None


#####
##      BALANCE DETAIL
#####
@dataclass
class BalanceDetail:
    id: int
    amount: float
    mode: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None


#####
##      LOG DETAIL
#####
@dataclass
class LogDetail:
    """Standardized log detail structure."""

    id: int
    method: str
    url: str
    status: str
    ip_address: str
    version: str
    provider: Provider
    source: str
    query: Optional[Dict[str, Any]] = None
    body: Optional[str] = None
    response: Optional[str] = None
    account_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


####
##      ALL LOGS RESPONSE
#####
@dataclass
class LogsResponse:
    """Standardized response structure for logs."""
    logs: List[LogDetail]
    meta: PaginationMeta


#####
##      WEBHOOK DETAIL
#####
@dataclass
class WebhookDetail:
    """Standardized webhook detail structure."""

    id: int
    url: str
    provider: Provider
    enabled: bool
    ssl_verify: bool
    disable_on_error: bool
    account_id: int
    http_headers: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


####
##      ALL WEBHOOK RESPONSE
#####
@dataclass
class WebhooksResponse:
    """Standardized response structure for webhooks."""
    webhooks: List[WebhookDetail]
    meta: PaginationMeta
