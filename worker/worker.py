"""
Worker service for processing trading signals
Polls the database for pending signals and executes trades via CCXT
"""
import os
import sys
import time
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import from backend
from app.models import Signal, Order, User, APIKey, Subscription
from app.crypto import get_crypto_manager

try:
    import ccxt
    from app.services.ccxt_client import CCXTClient
except ImportError:
    print("Warning: ccxt not installed. Install with: pip install ccxt")
    ccxt = None
    CCXTClient = None


# Environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://humbex:humbex_dev_password@localhost:5432/humbex"
)
WORKER_POLL_INTERVAL = int(os.getenv("WORKER_POLL_INTERVAL", "5"))
CCXT_TEST_MODE = os.getenv("CCXT_TEST_MODE", "true").lower() == "true"

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def log(message: str):
    """Log with timestamp"""
    print(f"[{datetime.utcnow().isoformat()}] {message}", flush=True)


def get_user_by_token(db: Session, token: str) -> Optional[User]:
    """Find user by token"""
    return db.query(User).filter(User.token == token).first()


def get_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """Check if user has active subscription"""
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active"
    ).first()


def get_active_api_key(db: Session, user_id: int) -> Optional[APIKey]:
    """Get user's active API key"""
    return db.query(APIKey).filter(
        APIKey.user_id == user_id,
        APIKey.is_active == True
    ).first()


def process_signal(db: Session, signal: Signal):
    """
    Process a single trading signal
    
    Steps:
    1. Find user by token
    2. Check active subscription
    3. Get decrypted API keys
    4. Execute trade via CCXT
    5. Record order in database
    """
    log(f"Processing signal {signal.id}: {signal.action} {signal.symbol} (token: {signal.token})")
    
    try:
        # Update status to processing
        signal.status = "processing"
        db.commit()
        
        # Find user by token
        user = get_user_by_token(db, signal.token)
        if not user:
            signal.status = "failed"
            signal.error_message = "User not found for token"
            signal.processed_at = datetime.utcnow()
            db.commit()
            log(f"  ✗ Signal {signal.id} failed: User not found")
            return
        
        signal.user_id = user.id
        db.commit()
        
        # Check active subscription
        subscription = get_active_subscription(db, user.id)
        if not subscription:
            signal.status = "failed"
            signal.error_message = "No active subscription"
            signal.processed_at = datetime.utcnow()
            db.commit()
            log(f"  ✗ Signal {signal.id} failed: No active subscription")
            return
        
        # Get API key
        api_key_record = get_active_api_key(db, user.id)
        if not api_key_record:
            signal.status = "failed"
            signal.error_message = "No active API key"
            signal.processed_at = datetime.utcnow()
            db.commit()
            log(f"  ✗ Signal {signal.id} failed: No active API key")
            return
        
        # Decrypt API credentials
        crypto_manager = get_crypto_manager()
        api_key = crypto_manager.decrypt(api_key_record.api_key_enc, api_key_record.iv)
        api_secret = crypto_manager.decrypt(api_key_record.api_secret_enc, api_key_record.iv)
        
        # Initialize CCXT client
        if CCXTClient is None:
            signal.status = "failed"
            signal.error_message = "CCXT not available"
            signal.processed_at = datetime.utcnow()
            db.commit()
            log(f"  ✗ Signal {signal.id} failed: CCXT not installed")
            return
        
        client = CCXTClient(
            api_key=api_key,
            api_secret=api_secret,
            test_mode=CCXT_TEST_MODE
        )
        
        # Format symbol for CCXT (e.g., AVAXUSDT -> AVAX/USDT:USDT)
        # Note: This assumes quote currency is always 4 characters (USDT)
        # TODO: Add more robust symbol parsing for different quote currencies
        symbol_formatted = f"{signal.symbol[:-4]}/{signal.symbol[-4:]}:{signal.symbol[-4:]}"
        
        # Execute trade based on action
        order_response = None
        
        if signal.action == "buy":
            if signal.price:
                order_response = client.create_limit_order(
                    symbol=symbol_formatted,
                    side="buy",
                    amount=signal.quantity or 1.0,
                    price=signal.price
                )
            else:
                order_response = client.create_market_order(
                    symbol=symbol_formatted,
                    side="buy",
                    amount=signal.quantity or 1.0
                )
        
        elif signal.action == "sell":
            if signal.price:
                order_response = client.create_limit_order(
                    symbol=symbol_formatted,
                    side="sell",
                    amount=signal.quantity or 1.0,
                    price=signal.price
                )
            else:
                order_response = client.create_market_order(
                    symbol=symbol_formatted,
                    side="sell",
                    amount=signal.quantity or 1.0
                )
        
        elif signal.action == "close":
            # Determine side based on current position (simplified: use sell to close long)
            # TODO: Query actual position to determine correct side (buy for short, sell for long)
            order_response = client.close_position(
                symbol=symbol_formatted,
                side="sell",
                amount=signal.quantity
            )
        
        # Record order
        order = Order(
            signal_id=signal.id,
            user_id=user.id,
            exchange=api_key_record.exchange,
            order_id=order_response.get('id'),
            symbol=signal.symbol,
            side=signal.action,
            order_type='limit' if signal.price else 'market',
            quantity=signal.quantity or 1.0,
            price=signal.price,
            filled_quantity=order_response.get('filled', 0.0),
            average_price=order_response.get('average'),
            status='filled' if order_response.get('status') == 'closed' else 'pending',
            test_mode=CCXT_TEST_MODE,
            created_at=datetime.utcnow()
        )
        
        db.add(order)
        
        # Update signal status
        signal.status = "completed"
        signal.processed_at = datetime.utcnow()
        db.commit()
        
        log(f"  ✓ Signal {signal.id} processed successfully (order: {order.order_id}, test_mode: {CCXT_TEST_MODE})")
    
    except Exception as e:
        signal.status = "failed"
        signal.error_message = str(e)
        signal.processed_at = datetime.utcnow()
        db.commit()
        log(f"  ✗ Signal {signal.id} failed: {str(e)}")


def run_worker():
    """Main worker loop"""
    log("=" * 60)
    log("HUMBEX Worker starting")
    log(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    log(f"Poll interval: {WORKER_POLL_INTERVAL}s")
    log(f"Test mode: {CCXT_TEST_MODE}")
    log("=" * 60)
    
    while True:
        db = None
        try:
            db = SessionLocal()
            
            # Fetch pending signals
            pending_signals = db.query(Signal).filter(
                Signal.status == "pending"
            ).order_by(Signal.received_at).all()
            
            if pending_signals:
                log(f"Found {len(pending_signals)} pending signal(s)")
                
                for signal in pending_signals:
                    process_signal(db, signal)
            
            # Wait before next poll
            time.sleep(WORKER_POLL_INTERVAL)
        
        except KeyboardInterrupt:
            log("Worker shutting down...")
            break
        
        except Exception as e:
            log(f"Worker error: {str(e)}")
            time.sleep(WORKER_POLL_INTERVAL)
        
        finally:
            if db:
                db.close()


if __name__ == "__main__":
    run_worker()
