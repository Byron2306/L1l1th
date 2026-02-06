"""Performance Agent - trading performance (realized/unrealized PnL, drawdown, win-rate)

This agent is deterministic and explainable. It rebuilds state from the Data Store
at startup, consumes fills (via `process_execution` called by the Coordinator), mark-to-
market from `latest_price` shared data, and emits `buzz.performance.snapshot` events.
"""

import threading
import time
import logging
import math
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
try:
    import psutil
except Exception:
    psutil = None


class PerformanceAgent:
    def __init__(self, coordinator: Optional[Any] = None, symbol: Optional[str] = None, emit_interval: int = 60):
        self.coordinator = coordinator
        self.symbol = symbol or (getattr(coordinator.cfg, 'symbol', None) if coordinator else None)
        self.emit_interval = emit_interval

        # Position state
        self.position_qty = 0.0
        self.avg_cost = 0.0
        self.realized_pnl = 0.0

        # Raw trade/fill history (keeps dicts with parsed fields)
        self.trades: List[Dict[str, Any]] = []

        # Dedup set for fills
        self._seen = set()

        # Equity baseline (from Data Store balances) used for pct metrics
        self.starting_equity = None

        # Background
        self._running = False
        self._thread = None

        # rolling snapshots cache
        self.last_snapshots: Dict[str, Dict[str, Any]] = {}

    # ------------------ startup / rebuild ------------------
    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._emit_loop, daemon=True)
            self._thread.start()
            # rebuild from Data Store
            try:
                self.rebuild_state()
            except Exception:
                logging.exception('PerformanceAgent.rebuild_state failed')
            logging.info('Performance Agent started')

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def rebuild_state(self, lookback: int = 1000, timeout: float = 5.0):
        """Rebuild state by querying recent fills and last balance from Data Store.

        Uses coordinator share/query contract to ask Data Store for `get_recent_fills`
        and the last recorded balance (via raw SQL). Waits for the `buzz.store.result`.
        """
        if not self.coordinator:
            return

        # query fills
        qid = f"perf-rebuild-{uuid.uuid4()}"
        qry = {'query_id': qid, 'name': 'get_recent_fills', 'params': {'limit': lookback}}
        try:
            self.coordinator.share_data('buzz.store.query', qry)
        except Exception:
            logging.exception('Failed to request recent fills from data store')

        deadline = time.time() + timeout
        fills = []
        while time.time() < deadline:
            res = self.coordinator.get_shared_data('buzz.store.result')
            if isinstance(res, dict) and res.get('payload', {}).get('query_id') == qid:
                if res.get('payload', {}).get('ok'):
                    fills = res.get('payload', {}).get('rows') or []
                break
            time.sleep(0.1)

        # rebuild position and realized pnl from fills
        try:
            # sort oldest -> newest
            fills_sorted = sorted(fills, key=lambda x: x.get('ts', x.get('timestamp', 0))) if fills else []
            for f in fills_sorted:
                # normalize keys (support dicts with different shapes)
                client_order_id = f.get('client_order_id') or f.get('clientId')
                order_id = f.get('order_id') or f.get('orderId')
                filled = float(f.get('filled_qty') or f.get('filled_qty') or f.get('filled') or f.get('quantity') or 0)
                price = float(f.get('avg_price') or f.get('avg_price') or f.get('price') or 0)
                fee = float(f.get('fee') or f.get('fees') or 0)
                side = (f.get('side') or '').upper() or (f.get('action') or '').upper()
                ts = f.get('ts') or f.get('timestamp') or 0
                key = (order_id or client_order_id or '') + f"|{filled}|{price}|{ts}"
                if key in self._seen:
                    continue
                self._seen.add(key)
                self._apply_fill(side, filled, price, fee)
                # keep copy
                self.trades.append({'ts': ts, 'side': side, 'filled': filled, 'price': price, 'fee': fee})
        except Exception:
            logging.exception('Failed rebuilding fills')

        # query last balance for baseline equity
        qid2 = f"perf-balance-{uuid.uuid4()}"
        sql = 'SELECT equity_usd_est FROM balances ORDER BY ts DESC LIMIT 1'
        try:
            self.coordinator.share_data('buzz.store.query', {'query_id': qid2, 'name': 'raw_sql', 'params': {'sql': sql}})
        except Exception:
            logging.exception('Failed to request last balance')

        deadline = time.time() + timeout
        while time.time() < deadline:
            res = self.coordinator.get_shared_data('buzz.store.result')
            if isinstance(res, dict) and res.get('payload', {}).get('query_id') == qid2:
                rows = res.get('payload', {}).get('rows') or []
                if rows and isinstance(rows, list) and len(rows) > 0:
                    # rows may be list of dicts or tuples
                    r0 = rows[0]
                    if isinstance(r0, dict):
                        self.starting_equity = float(r0.get('equity_usd_est') or r0.get('equity'))
                    elif isinstance(r0, (list, tuple)):
                        try:
                            self.starting_equity = float(r0[0])
                        except Exception:
                            self.starting_equity = None
                break
            time.sleep(0.1)

    # ------------------ fill processing ------------------
    def process_execution(self, evt: Dict[str, Any]):
        """Process a `buzz.trade.execution` event payload (dict). Intended to be called
        by the Coordinator when an execution event is received.
        """
        try:
            p = evt.get('payload') if isinstance(evt, dict) else evt
            if not p:
                return
            side = (p.get('side') or '').upper() or (p.get('action') or '').upper()
            filled = float(p.get('filled_qty') or p.get('filled') or 0)
            price = float(p.get('avg_price') or p.get('price') or 0)
            fee = float(p.get('fees') or p.get('fee') or 0)
            order_id = p.get('order_id') or p.get('orderId') or ''
            client_order_id = p.get('client_order_id') or p.get('clientId') or ''
            ts = p.get('ts') or int(time.time()*1000)

            key = (order_id or client_order_id or '') + f"|{filled}|{price}|{ts}"
            if key in self._seen:
                logging.debug(f"Duplicate fill skipped: {key}")
                return
            self._seen.add(key)

            # apply fill to state
            self._apply_fill(side, filled, price, fee)

            # append trade record
            self.trades.append({'ts': ts, 'side': side, 'filled': filled, 'price': price, 'fee': fee})

        except Exception:
            logging.exception('PerformanceAgent.process_execution failed')

    def _apply_fill(self, side: str, qty: float, price: float, fee: float):
        try:
            if qty <= 0:
                return
            if side == 'BUY':
                # increase position and update avg cost
                prev_qty = self.position_qty
                prev_cost = self.avg_cost
                new_qty = prev_qty + qty
                if new_qty > 0:
                    self.avg_cost = (prev_cost * prev_qty + price * qty) / new_qty
                else:
                    self.avg_cost = 0.0
                self.position_qty = new_qty
                # fees reduce cash/equity; treat as realized drag only when position is closed
                # we subtract fee immediately from realized_pnl (conservative)
                self.realized_pnl -= fee
            elif side == 'SELL':
                # realized pnl = (sell_price - avg_cost) * qty - fee
                realized = (price - self.avg_cost) * qty - fee
                self.realized_pnl += realized
                self.position_qty = max(0.0, self.position_qty - qty)
                if self.position_qty == 0:
                    self.avg_cost = 0.0
            else:
                # unknown side: ignore
                pass
        except Exception:
            logging.exception('_apply_fill failed')

    # ------------------ metrics / snapshots ------------------
    def _compute_window_metrics(self, window_seconds: int) -> Dict[str, Any]:
        now_ts = int(time.time() * 1000)
        cutoff = now_ts - (window_seconds * 1000)
        window_trades = [t for t in self.trades if (t.get('ts') or 0) >= cutoff]

        trades_count = len(window_trades)
        sells = [t for t in window_trades if (t.get('side') or '').upper() == 'SELL']
        wins = 0
        total_fees = 0.0
        total_pnl = 0.0
        for t in sells:
            # estimate per-trade realized: since we only store aggregated realized on sells, approximate by (price-avg_cost)*qty - fee
            qty = float(t.get('filled') or 0)
            price = float(t.get('price') or 0)
            fee = float(t.get('fee') or 0)
            pnl = (price - self.avg_cost) * qty - fee
            total_pnl += pnl
            total_fees += fee
            if pnl > 0:
                wins += 1

        win_rate = (wins / len(sells)) if sells else None
        avg_fee = (total_fees / trades_count) if trades_count else 0.0

        # compute equity estimate
        mark_price = self.coordinator.get_shared_data('latest_price') if self.coordinator else None
        unrealized = 0.0
        if mark_price is not None and self.position_qty:
            try:
                m = float(mark_price)
                unrealized = (m - self.avg_cost) * self.position_qty
            except Exception:
                unrealized = 0.0

        equity_est = None
        if self.starting_equity is not None:
            equity_est = float(self.starting_equity) + self.realized_pnl + unrealized
        else:
            # fallback: use realized + unrealized as equity change from zero baseline
            equity_est = self.realized_pnl + unrealized

        # simplistic drawdown: compute peak-to-trough over recorded equity points (approximate)
        equity_points = []
        e = float(self.starting_equity or 0.0)
        for t in sorted(self.trades, key=lambda x: x.get('ts', 0)):
            s = (t.get('side') or '').upper()
            if s == 'BUY':
                e += 0  # conservative
            elif s == 'SELL':
                qty = float(t.get('filled') or 0)
                price = float(t.get('price') or 0)
                fee = float(t.get('fee') or 0)
                e += (price - self.avg_cost) * qty - fee
            equity_points.append(e)

        max_drawdown_pct = 0.0
        if equity_points:
            peak = equity_points[0]
            trough = peak
            max_dd = 0.0
            for v in equity_points:
                if v > peak:
                    peak = v
                    trough = v
                if v < trough:
                    trough = v
                    if peak > 0:
                        max_dd = max(max_dd, (peak - trough) / peak * 100)
            max_drawdown_pct = max_dd

        pnl_pct = None
        try:
            if self.starting_equity and self.starting_equity != 0:
                pnl_pct = (equity_est - float(self.starting_equity)) / float(self.starting_equity) * 100
        except Exception:
            pnl_pct = None

        return {
            'symbol': self.symbol,
            'window': f"{window_seconds}s",
            'equity_usd_est': round(equity_est, 6) if equity_est is not None else None,
            'realized_pnl_usd': round(self.realized_pnl, 6),
            'unrealized_pnl_usd': round(unrealized, 6),
            'pnl_pct': round(pnl_pct, 4) if pnl_pct is not None else None,
            'max_drawdown_pct': round(max_drawdown_pct, 4),
            'win_rate': round(win_rate, 4) if win_rate is not None else None,
            'trades': trades_count,
            'avg_fee_usd': round(avg_fee, 6)
        }

    def _emit_loop(self):
        while self._running:
            try:
                # emit for 5m,1h,1d
                for ws in (300, 3600, 86400):
                    metrics = self._compute_window_metrics(ws)
                    now_ms = int(time.time() * 1000)
                    evt = {'buzz': {'type': 'buzz.performance.snapshot', 'source': 'PERFORMANCE', 'ts': now_ms}, 'payload': metrics}
                    try:
                        if self.coordinator:
                            self.coordinator.share_data('buzz.performance.snapshot', evt)
                    except Exception:
                        logging.exception('Failed to share performance snapshot')
                    # simple alerting against coordinator-configured thresholds
                    try:
                        cfg = getattr(self.coordinator, 'cfg', None)
                        if cfg:
                            dd_pct = metrics.get('max_drawdown_pct', 0)
                            # convert pct numbers if necessary
                            if isinstance(dd_pct, str):
                                dd_pct = float(dd_pct)
                            if getattr(cfg, 'daily_loss_halt_pct', None) is not None:
                                halt_threshold = abs(getattr(cfg, 'daily_loss_halt_pct')) * 100 if getattr(cfg, 'daily_loss_halt_pct') < 0 else getattr(cfg, 'daily_loss_halt_pct')
                                throttle_threshold = abs(getattr(cfg, 'daily_loss_throttle_pct')) * 100 if getattr(cfg, 'daily_loss_throttle_pct') < 0 else getattr(cfg, 'daily_loss_throttle_pct')
                                if dd_pct >= (halt_threshold or 300):
                                    alert = {'level': 'HALT', 'reason': 'drawdown_exceeded', 'value': dd_pct}
                                    try:
                                        self.coordinator.share_data('buzz.performance.alert', {'buzz': {'type': 'buzz.performance.alert', 'source': 'PERFORMANCE', 'ts': now_ms}, 'payload': alert})
                                    except Exception:
                                        pass
                                elif dd_pct >= (throttle_threshold or 150):
                                    alert = {'level': 'THROTTLE', 'reason': 'drawdown_high', 'value': dd_pct}
                                    try:
                                        self.coordinator.share_data('buzz.performance.alert', {'buzz': {'type': 'buzz.performance.alert', 'source': 'PERFORMANCE', 'ts': now_ms}, 'payload': alert})
                                    except Exception:
                                        pass
                    except Exception:
                        pass

                time.sleep(self.emit_interval)
            except Exception:
                logging.exception('PerformanceAgent._emit_loop error')
                time.sleep(self.emit_interval)

    # ------------------ lightweight observability APIs ------------------
    def track_system_metrics(self):
        """Collect simple system metrics (cpu / memory) for UI display."""
        try:
            cpu = psutil.cpu_percent(interval=None) if psutil else 0.0
            mem = psutil.virtual_memory().percent if psutil else 0.0
        except Exception:
            cpu = 0.0
            mem = 0.0
        now = int(time.time() * 1000)
        self.last_snapshots['system_metrics'] = {'cpu_percent': cpu, 'memory_percent': mem, 'ts': now}

    def track_response_time(self, name: str, start_time: float):
        """Record a response time for a named operation (seconds)."""
        try:
            elapsed = max(0.0, time.time() - float(start_time))
        except Exception:
            elapsed = None
        self.last_snapshots.setdefault('response_times', {})[name] = elapsed

    def get_current_metrics(self) -> Dict[str, Any]:
        """Return aggregated metrics for UI consumption."""
        out = {}
        sys = self.last_snapshots.get('system_metrics') or {}
        out['cpu_percent'] = sys.get('cpu_percent')
        out['memory_percent'] = sys.get('memory_percent')
        out['response_times'] = self.last_snapshots.get('response_times', {})
        return out
