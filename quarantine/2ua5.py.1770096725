"""
Lightweight entry point for launching the Flask dashboard without running the
full trading loop. Useful for editing configuration and API keys when the rest
of the system isn't running.
"""

import logging
import time
import ccxt

from main import load_config
from agents.coordinator import SwarmCoordinator


def launch_ui_only() -> None:
    """Start the UI Agent and keep the process alive."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    cfg = load_config()

    # Force UI on and disable heavy/optional agents so the dashboard can run
    # even when trading dependencies (Binance client, database, encryption key)
    # aren't available.
    cfg.ui_enabled = True
    cfg.kill_switch_enabled = False
    cfg.network_enabled = False
    cfg.data_store_enabled = False
    cfg.performance_enabled = False
    cfg.security_enabled = False
    # Prevent wallet monitor from attempting RPC connections in UI-only mode
    cfg.web3_rpc_url = None
    cfg.watch_address = None

    coordinator = SwarmCoordinator(cfg)

    # Initialize a public client so market data (and wallet monitor) can run in UI-only mode.
    client = None
    try:
        if cfg.exchange.lower() == "kraken":
            client = ccxt.kraken({"enableRateLimit": True})
        else:
            from binance.client import Client
            client = Client(cfg.binance_api_key, cfg.binance_api_secret)
            if cfg.binance_testnet:
                client.API_URL = "https://testnet.binance.vision/api"
    except Exception as e:
        logging.warning(f"UI-only exchange client init failed: {e}")

    if client:
        coordinator.initialize(client)

    coordinator.start_background_tasks()

    logging.info("UI available at http://%s:%s", cfg.ui_host, cfg.ui_port)
    logging.info("Press Ctrl+C to stop the UI.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        coordinator.running = False
        if coordinator.agents.get("ui"):
            coordinator.agents["ui"].stop()
        logging.info("UI stopped.")


if __name__ == "__main__":
    launch_ui_only()
