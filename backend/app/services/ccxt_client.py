"""
CCXT Client wrapper for Bybit trading
Supports dry-run/test mode by default
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import ccxt
except ImportError:
    ccxt = None


class CCXTClient:
    """
    Wrapper for CCXT Bybit exchange client
    
    Features:
    - Dry-run mode by default (test_mode=True)
    - Support for perpetual futures trading
    - Order placement and status checking
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        test_mode: bool = True
    ):
        """
        Initialize CCXT client
        
        Args:
            api_key: Bybit API key (decrypted)
            api_secret: Bybit API secret (decrypted)
            test_mode: If True, uses testnet/dry-run mode
        """
        if ccxt is None:
            raise ImportError("ccxt library not installed. Install with: pip install ccxt")
        
        self.test_mode = test_mode
        
        # Initialize Bybit exchange
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Perpetual futures
            }
        })
        
        # Use testnet if in test mode
        if test_mode:
            self.exchange.set_sandbox_mode(True)
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a market order
        
        Args:
            symbol: Trading pair (e.g., 'AVAX/USDT:USDT')
            side: 'buy' or 'sell'
            amount: Order quantity
            params: Additional parameters
            
        Returns:
            Order response from exchange
        """
        if self.test_mode:
            # Simulate order in test mode
            return {
                'id': f'test_{datetime.utcnow().timestamp()}',
                'symbol': symbol,
                'side': side,
                'type': 'market',
                'amount': amount,
                'status': 'closed',
                'filled': amount,
                'average': 0.0,
                'info': {'test_mode': True}
            }
        
        return self.exchange.create_market_order(
            symbol=symbol,
            side=side,
            amount=amount,
            params=params or {}
        )
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a limit order
        
        Args:
            symbol: Trading pair (e.g., 'AVAX/USDT:USDT')
            side: 'buy' or 'sell'
            amount: Order quantity
            price: Limit price
            params: Additional parameters
            
        Returns:
            Order response from exchange
        """
        if self.test_mode:
            # Simulate order in test mode
            return {
                'id': f'test_{datetime.utcnow().timestamp()}',
                'symbol': symbol,
                'side': side,
                'type': 'limit',
                'amount': amount,
                'price': price,
                'status': 'open',
                'filled': 0.0,
                'average': 0.0,
                'info': {'test_mode': True}
            }
        
        return self.exchange.create_limit_order(
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            params=params or {}
        )
    
    def close_position(
        self,
        symbol: str,
        side: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Close an open position
        
        Args:
            symbol: Trading pair (e.g., 'AVAX/USDT:USDT')
            side: 'buy' to close short, 'sell' to close long
            amount: Position size to close (None for full position)
            
        Returns:
            Order response from exchange
        """
        if self.test_mode:
            # Simulate position close in test mode
            return {
                'id': f'test_close_{datetime.utcnow().timestamp()}',
                'symbol': symbol,
                'side': side,
                'type': 'market',
                'amount': amount or 0.0,
                'status': 'closed',
                'filled': amount or 0.0,
                'info': {'test_mode': True, 'position_close': True}
            }
        
        # Get position info if amount not specified
        if amount is None:
            positions = self.exchange.fetch_positions([symbol])
            position = next((p for p in positions if p['symbol'] == symbol), None)
            if position:
                amount = abs(position['contracts'])
        
        # Create market order to close position
        return self.create_market_order(
            symbol=symbol,
            side=side,
            amount=amount,
            params={'reduce_only': True}
        )
    
    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Fetch order status
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            Order information
        """
        if self.test_mode:
            return {
                'id': order_id,
                'symbol': symbol,
                'status': 'closed',
                'info': {'test_mode': True}
            }
        
        return self.exchange.fetch_order(order_id, symbol)
    
    def fetch_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance
        
        Returns:
            Balance information
        """
        if self.test_mode:
            return {
                'USDT': {
                    'free': 10000.0,
                    'used': 0.0,
                    'total': 10000.0
                },
                'info': {'test_mode': True}
            }
        
        return self.exchange.fetch_balance()
