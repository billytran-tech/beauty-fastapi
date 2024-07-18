from enum import Enum


class PaymentStatusEnum(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CHARGEBACK = "chargeback"


class BookingStatusEnum(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"
    REJECTED = "rejected"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    NO_SHOW = "no_show"


class PaymentGatewayEnum(str, Enum):
    STRIPE = "stripe"


class TransactionTypeEnum(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    CHARGEBACK = "chargeback"


class TransactionStatusEnum(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CHARGEBACK = "chargeback"
