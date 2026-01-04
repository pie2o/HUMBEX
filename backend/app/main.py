import os
import hmac
import hashlib
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .db import get_db, engine, Base
from .models import Signal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
    yield


app = FastAPI(
    title="HUMBEX API",
    description="AVAXUSDT Perpetual Trading Bot - TradingView Webhook Receiver",
    version="1.0.0",
    lifespan=lifespan
)

# Environment variables
TRADINGVIEW_SECRET = os.getenv("TRADINGVIEW_SECRET", "changeme")


class WebhookPayload(BaseModel):
    """TradingView webhook payload model"""
    token: str = Field(..., description="User token for identification")
    action: str = Field(..., description="Trading action: buy, sell, or close")
    symbol: str = Field(..., description="Trading symbol, e.g., AVAXUSDT")
    quantity: Optional[float] = Field(None, description="Order quantity")
    price: Optional[float] = Field(None, description="Limit price (optional)")


def verify_signature(body: bytes, signature: str) -> bool:
    """
    Verify HMAC-SHA256 signature from TradingView webhook
    
    Args:
        body: Raw request body bytes
        signature: Hex-encoded HMAC signature from X-Signature header
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = hmac.new(
        TRADINGVIEW_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature.lower(), expected_signature.lower())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "humbex-backend",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/webhook")
async def webhook_handler(request: Request, payload: WebhookPayload):
    """
    TradingView webhook endpoint
    
    Receives trading signals from TradingView and stores them in the database
    for processing by the worker service.
    
    Headers:
        X-Signature: HMAC-SHA256 signature of the request body
    
    Body:
        token: User token
        action: Trading action (buy/sell/close)
        symbol: Trading symbol
        quantity: Order quantity (optional)
        price: Limit price (optional)
    """
    # Get signature from header
    signature = request.headers.get("X-Signature", "")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Signature header"
        )
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature
    if not verify_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Validate action
    valid_actions = ["buy", "sell", "close"]
    if payload.action.lower() not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        )
    
    # Store signal in database
    db: Session = next(get_db())
    
    try:
        signal = Signal(
            token=payload.token,
            action=payload.action.lower(),
            symbol=payload.symbol.upper(),
            quantity=payload.quantity,
            price=payload.price,
            status="pending",
            received_at=datetime.utcnow()
        )
        
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        return {
            "status": "success",
            "message": "Signal received and queued for processing",
            "signal_id": signal.id,
            "timestamp": signal.received_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store signal: {str(e)}"
        )
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "HUMBEX API",
        "version": "1.0.0",
        "description": "AVAXUSDT Perpetual Trading Bot",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
