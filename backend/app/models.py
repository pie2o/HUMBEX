from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    signals = relationship("Signal", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Subscription(Base):
    """User subscription status"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="inactive")  # active, inactive, expired
    expires_at = Column(DateTime, nullable=True)
    payment_reference = Column(String(255), nullable=True)  # MEXC payment reference
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


class APIKey(Base):
    """Encrypted Bybit API keys"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False, default="bybit")  # Exchange name
    api_key_enc = Column(Text, nullable=False)  # Encrypted API key
    api_secret_enc = Column(Text, nullable=False)  # Encrypted API secret
    iv = Column(String(32), nullable=False)  # Initialization vector for AES-GCM
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class Signal(Base):
    """TradingView webhook signals"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(100), nullable=False, index=True)  # User token from webhook
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Resolved user (can be null if token not found)
    action = Column(String(20), nullable=False)  # buy, sell, close
    symbol = Column(String(50), nullable=False)  # AVAXUSDT
    quantity = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="signals")
    orders = relationship("Order", back_populates="signal")


class Order(Base):
    """Trade execution records"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False, default="bybit")
    order_id = Column(String(100), nullable=True)  # Exchange order ID
    symbol = Column(String(50), nullable=False)
    side = Column(String(20), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    filled_quantity = Column(Float, default=0.0, nullable=True)
    average_price = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, filled, partial, cancelled, failed
    test_mode = Column(Boolean, default=True, nullable=False)  # Dry-run flag
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    signal = relationship("Signal", back_populates="orders")
    user = relationship("User", back_populates="orders")
