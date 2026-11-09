from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models in Campus Byte.
    
    Future models to inherit from this Base:
    - User (Core authentication and user details)
    - Restaurant (Campus restaurants / food outlets)
    - MenuItem (Menu offerings, prices, categories, availability)
    - Order (Customer orders and billing)
    - OrderItem (Individual order line items)
    - DeliveryPartner (Delivery fleet profiles and status)
    - DeliveryAssignment (Order-to-partner assignments)
    - OrderStatusHistory (Audit trail for order state progression)
    """
    pass
