from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    RESTAURANT_OWNER = "RESTAURANT_OWNER"
    DELIVERY_PARTNER = "DELIVERY_PARTNER"


class VehicleType(str, Enum):
    BICYCLE = "BICYCLE"
    SCOOTER = "SCOOTER"
    WALKING = "WALKING"
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class DeliveryStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
