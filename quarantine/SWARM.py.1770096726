#!/usr/bin/env python3
"""
Educational SMA-crossover trading agent template:
- Market data: Binance klines (historical + near-real-time via polling)
- Price sanity check: CoinGecko spot
- Trading: Binance Spot market orders
- Wallet monitoring: Web3.py (ETH + optional ERC-20 read)
SAFE DEFAULT: DRY_RUN=1 (no real orders).

Requirements:
  pip install python-binance web3 requests python-dotenv

Environment variables (recommended in a .env file):
  BINANCE_API_KEY=...
  BINANCE_API_SECRET=...
  BINANCE_TESTNET=1            # 1 to use testnet endpoints (recommended)
  DRY_RUN=1                    # 1 => no orders sent
  SYMBOL=BTCUSDT
  INTERVAL=1m                  # Binance kline interval (e.g., 1m, 5m, 1h)
  LOOKBACK=500                 # number of candles to fetch
  SMA_FAST=20
  SMA_SLOW=50
  QUOTE_ORDER_SIZE=25          # spend this many USDT per buy (example)
  MAX_POSITION_BASE=0.002      # cap base asset position size (example)
  POLL_SECONDS=10

Wallet (optional):
  WEB3_RPC_URL=https://mainnet.infura.io/v3/1e9d15da10144e0cabee4dd3c10b3014
  WATCH_ADDRESS=0x7Ba65b768bdeae6F29213e30daa0152583A591aF
  ERC20_TOKEN_ADDRESS=0xTokenAddressToWatch   # optional
"""

import os
import time
import math
import json
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List

import requests
from dotenv import load_dotenv

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from web3 import Web3

# -----------------------------
# Config
# -----------------------------

@dataclass
class Config:
    binance_api_key: str
    binance_api_secret: str
    binance_testnet: bool

    dry_run: bool

    symbol: str
    interval: str
    lookback: int

    sma_fast: int
    sma_slow: int

    quote_order_size: float          # e.g., USDT amount to spend per buy
    max_position_base: float         # cap base position size

    poll_seconds: int

    # Optional wallet monitoring
    web3_rpc_url: Optional[str]
    watch_address: Optional[str]
    erc20_token_address: Optional[str]


def load_config() -> Config:
    load_dotenv()

    def getenv_bool(key: str, default: str = "0") -> bool:
        return os.getenv(key, default).strip() in ("1", "true", "True", "yes", "YES")

    return Config(
        binance_api_key=os.environ.get("BINANCE_API_KEY", ""),
        binance_api_secret=os.environ.get("BINANCE_API_SECRET", ""),
        binance_testnet=getenv_bool("BINANCE_TESTNET", "1"),

        dry_run=getenv_bool("DRY_RUN", "1"),

        symbol=os.environ.get("SYMBOL", "BTCUSDT"),
        interval=os.environ.get("INTERVAL", "1m"),
        lookback=int(os.environ.get("LOOKBACK", "500")),

        sma_fast=int(os.environ.get("SMA_FAST", "20")),
        sma_slow=int(os.environ.get("SMA_SLOW", "50")),

        quote_order_size=float(os.environ.get("QUOTE_ORDER_SIZE", "25")),
        max_position_base=float(os.environ.get("MAX_POSITION_BASE", "0.002")),

        poll_seconds=int(os.environ.get("POLL_SECONDS", "10")),

        web3_rpc_url=os.environ.get("WEB3_RPC_URL"),
        watch_address=os.environ.get("WATCH_ADDRESS"),
        erc20_token_address=os.environ.get("ERC20_TOKEN_ADDRESS"),
    )


# -----------------------------
# Logging
# -----------------------------

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# -----------------------------
# Helpers
# -----------------------------

def sma(values: List[float], window: int) -> List[Optional[float]]:
    """Simple moving average. Returns list aligned with input; leading Nones."""
    if window <= 0:
        raise ValueError("window must be > 0")
    out: List[Optional[float]] = [None] * len(values)
    if len(values) < window:
        return out

    running = sum(values[:window])
    out[window - 1] = running / window
    for i in range(window, len(values)):
        running += values[i] - values[i - window]
        out[i] = running / window
    return out


def round_step_size(quantity: float, step_size: float) -> float:
    """Rounds down to the nearest step size."""
    if step_size <= 0:
        return quantity
    precision = int(round(-math.log(step_size, 10), 0))
    return math.floor(quantity * (10 ** precision)) / (10 ** precision)


# -----------------------------
# Data: Binance + CoinGecko
# -----------------------------

class MarketData:
    def __init__(self, client: Client, symbol: str, interval: str):
        self.client = client
        self.symbol = symbol
        self.interval = interval

    def fetch_closes(self, limit: int) -> Tuple[List[int], List[float]]:
        """
        Fetch recent klines and return (close_times, closes).
        Kline format: [
          [ open_time, open, high, low, close, volume, close_time, ... ],
          ...
        ]
        """
        klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=limit)
        close_times = [int(k[6]) for k in klines]   # close_time
        closes = [float(k[4]) for k in klines]      # close
        return close_times, closes

    def fetch_latest_price(self) -> float:
        ticker = self.client.get_symbol_ticker(symbol=self.symbol)
        return float(ticker["price"])


class CoinGeckoData:
    """
    Optional sanity-check spot price from CoinGecko.
    Note: CoinGecko uses coin ids; mapping symbols robustly is non-trivial.
    This example supports a few common coins.
    """
    SYMBOL_TO_COINGECKO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "ADA": "cardano",
        "XRP": "ripple",
        "DOGE": "dogecoin",
    }

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def spot_price_usd(self, base_symbol: str) -> Optional[float]:
        coin_id = self.SYMBOL_TO_COINGECKO_ID.get(base_symbol.upper())
        if not coin_id:
            return None
        url = f"{self.base_url}/simple/price"
        r = requests.get(url, params={"ids": coin_id, "vs_currencies": "usd"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return float(data[coin_id]["usd"])


# -----------------------------
# Wallet monitoring (Web3.py)
# -----------------------------

ERC20_MIN_ABI = json.loads("""
[
  {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
  {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},
  {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
]
""")

class WalletMonitor:
    def __init__(self, rpc_url: str, watch_address: str, erc20_token_address: Optional[str] = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise RuntimeError("Web3 provider not connected. Check WEB3_RPC_URL.")
        self.addr = self.w3.to_checksum_address(watch_address)

        self.token = None
        self.token_symbol = None
        self.token_decimals = None
        if erc20_token_address:
            taddr = self.w3.to_checksum_address(erc20_token_address)
            self.token = self.w3.eth.contract(address=taddr, abi=ERC20_MIN_ABI)
            try:
                self.token_symbol = self.token.functions.symbol().call()
                self.token_decimals = self.token.functions.decimals().call()
            except Exception:
                self.token_symbol = "ERC20"
                self.token_decimals = 18

    def eth_balance(self) -> float:
        wei = self.w3.eth.get_balance(self.addr)
        return float(self.w3.from_wei(wei, "ether"))

    def erc20_balance(self) -> Optional[float]:
        if not self.token:
            return None
        raw = self.token.functions.balanceOf(self.addr).call()
        return float(raw) / (10 ** int(self.token_decimals or 18))


# -----------------------------
# Strategy: SMA crossover
# -----------------------------

class SMACrossoverStrategy:
    """
    Signal rules:
      - BUY when fast SMA crosses above slow SMA
      - SELL when fast SMA crosses below slow SMA
    """
    def __init__(self, fast: int, slow: int):
        if fast >= slow:
            raise ValueError("SMA_FAST must be < SMA_SLOW for crossover logic.")
        self.fast = fast
        self.slow = slow

    def signal(self, closes: List[float]) -> str:
        if len(closes) < self.slow + 2:
            return "HOLD"

        fast_s = sma(closes, self.fast)
        slow_s = sma(closes, self.slow)

        # Use last two points to detect cross
        f1, f2 = fast_s[-2], fast_s[-1]
        s1, s2 = slow_s[-2], slow_s[-1]
        if f1 is None or f2 is None or s1 is None or s2 is None:
            return "HOLD"

        crossed_up = (f1 <= s1) and (f2 > s2)
        crossed_down = (f1 >= s1) and (f2 < s2)

        if crossed_up:
            return "BUY"
        if crossed_down:
            return "SELL"
        return "HOLD"


# -----------------------------
# Trader: Binance execution
# -----------------------------

class BinanceTrader:
    def __init__(self, client: Client, symbol: str, dry_run: bool, max_position_base: float):
        self.client = client
        self.symbol = symbol
        self.dry_run = dry_run
        self.max_position_base = max_position_base

        # Infer base/quote assets from symbol info
        info = self.client.get_symbol_info(symbol)
        if not info:
            raise RuntimeError(f"Unknown symbol: {symbol}")
        self.base_asset = info["baseAsset"]
        self.quote_asset = info["quoteAsset"]
        self.filters = {f["filterType"]: f for f in info["filters"]}

    def _get_step_size(self) -> float:
        lot = self.filters.get("LOT_SIZE")
        return float(lot["stepSize"]) if lot else 0.0

    def balances(self) -> Tuple[float, float]:
        base_free = float(self.client.get_asset_balance(asset=self.base_asset)["free"])
        quote_free = float(self.client.get_asset_balance(asset=self.quote_asset)["free"])
        return base_free, quote_free

    def buy_market_quote(self, quote_amount: float) -> None:
        """
        Place MARKET BUY using quoteOrderQty (spend quote asset).
        This is generally simpler than computing base qty.
        """
        if self.dry_run:
            logging.info(f"[DRY_RUN] BUY {self.symbol} spending ~{quote_amount} {self.quote_asset}")
            return
        try:
            order = self.client.order_market_buy(symbol=self.symbol, quoteOrderQty=quote_amount)
            logging.info(f"BUY order placed: {order}")
        except (BinanceAPIException, BinanceOrderException) as e:
            logging.error(f"BUY failed: {e}")

    def sell_market_base(self, base_qty: float) -> None:
        step = self._get_step_size()
        qty = round_step_size(base_qty, step)
        if qty <= 0:
            logging.info("Sell qty rounded to 0; skipping.")
            return

        if self.dry_run:
            logging.info(f"[DRY_RUN] SELL {self.symbol} amount {qty} {self.base_asset}")
            return
        try:
            order = self.client.order_market_sell(symbol=self.symbol, quantity=qty)
            logging.info(f"SELL order placed: {order}")
        except (BinanceAPIException, BinanceOrderException) as e:
            logging.error(f"SELL failed: {e}")


# -----------------------------
# Main loop
# -----------------------------

def main():
    setup_logging()
    cfg = load_config()

    if not cfg.binance_api_key or not cfg.binance_api_secret:
        raise SystemExit("Missing BINANCE_API_KEY / BINANCE_API_SECRET.")

    client = Client(cfg.binance_api_key, cfg.binance_api_secret)

    # Testnet routing (python-binance supports setting API URL)
    if cfg.binance_testnet:
        client.API_URL = "https://testnet.binance.vision/api"

    data = MarketData(client, cfg.symbol, cfg.interval)
    cg = CoinGeckoData()

    wallet = None
    if cfg.web3_rpc_url and cfg.watch_address:
        try:
            wallet = WalletMonitor(cfg.web3_rpc_url, cfg.watch_address, cfg.erc20_token_address)
            logging.info("Wallet monitor enabled.")
        except Exception as e:
            logging.warning(f"Wallet monitor disabled (error): {e}")

    strategy = SMACrossoverStrategy(cfg.sma_fast, cfg.sma_slow)
    trader = BinanceTrader(client, cfg.symbol, cfg.dry_run, cfg.max_position_base)

    logging.info(
        f"Starting agent | symbol={cfg.symbol} interval={cfg.interval} "
        f"fast={cfg.sma_fast} slow={cfg.sma_slow} lookback={cfg.lookback} "
        f"testnet={cfg.binance_testnet} dry_run={cfg.dry_run}"
    )

    last_close_time = None

    while True:
        try:
            close_times, closes = data.fetch_closes(cfg.lookback)
            if not close_times:
                logging.warning("No candles returned; retrying.")
                time.sleep(cfg.poll_seconds)
                continue

            latest_close_time = close_times[-1]
            latest_price = closes[-1]

            # Only act once per new candle close (prevents over-trading on same candle)
            if last_close_time == latest_close_time:
                time.sleep(cfg.poll_seconds)
                continue
            last_close_time = latest_close_time

            sig = strategy.signal(closes)
            base_free, quote_free = trader.balances()

            # Optional CoinGecko sanity check (USD spot)
            base_sym = trader.base_asset
            cg_usd = cg.spot_price_usd(base_sym)
            cg_note = f" | CoinGecko {base_sym}/USD={cg_usd:.2f}" if cg_usd else ""

            # Optional wallet readout
            wallet_note = ""
            if wallet:
                eth_bal = wallet.eth_balance()
                tok_bal = wallet.erc20_balance()
                if tok_bal is not None:
                    wallet_note = f" | Wallet ETH={eth_bal:.4f}, {wallet.token_symbol}={tok_bal:.4f}"
                else:
                    wallet_note = f" | Wallet ETH={eth_bal:.4f}"

            logging.info(
                f"Candle closed @ {latest_close_time} | price={latest_price:.2f} "
                f"| signal={sig} | Binance bal: {base_sym}={base_free:.6f} {trader.quote_asset}={quote_free:.2f}"
                f"{cg_note}{wallet_note}"
            )

            # Simple risk controls / position caps
            if sig == "BUY":
                if base_free >= cfg.max_position_base:
                    logging.info("BUY skipped: already at/above max base position cap.")
                elif quote_free < cfg.quote_order_size:
                    logging.info("BUY skipped: insufficient quote balance.")
                else:
                    # Example: spend fixed quote amount
                    trader.buy_market_quote(cfg.quote_order_size)

            elif sig == "SELL":
                if base_free <= 0:
                    logging.info("SELL skipped: no base balance.")
                else:
                    # Example: sell all base (or tune to partial)
                    trader.sell_market_base(base_free)

            # HOLD: do nothing

        except Exception as e:
            logging.error(f"Loop error: {e}")

        time.sleep(cfg.poll_seconds)


if __name__ == "__main__":
    main()
