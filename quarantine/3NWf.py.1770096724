import redis
import json
import logging
import uuid
import threading
import time
from collections import OrderedDict, defaultdict
from typing import Any, Dict, Optional, Callable


class NetworkAgent:
    """Network Agent: Redis Streams wrapper implementing a simple Buzz Bus.

    Features:
    - publish(topic, message): XADD to stream
    - subscribe(topic, handler, group=None): XREADGROUP loop with ack
    - envelope normalization (buzz.id, buzz.ts, buzz.type, buzz.source)
    - simple dedupe via in-memory LRU of recent buzz.ids
    - health publishing (`buzz.net.health`) via `publish_health`
    Falls back to simple Redis PUB/SUB and caching when streams are unavailable.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None, consumer_group_pref: str = "swarm_group"):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client: Optional[redis.Redis] = None
        self.consumer_group_pref = consumer_group_pref
        self._connect()

        # dedupe cache (LRU) of recently seen buzz ids
        self._seen = OrderedDict()
        self._seen_max = 2000

        # threads for subscribers
        self._subs_threads = []
        self._stop = threading.Event()

        # track consumer metadata
        self._consumers = defaultdict(list)  # topic -> list of (group, consumer_name)

        # health thread
        self._health_interval = 30
        self._health_thread = threading.Thread(target=self._health_loop, daemon=True)
        self._health_thread.start()

    def _connect(self):
        """Establish Redis connection."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # For string responses
            )
            # test connection
            self.client.ping()
            logging.info(f"Network Agent connected to Redis at {self.host}:{self.port}")
            try:
                self.pubsub = self.client.pubsub()
            except Exception:
                self.pubsub = None
        except redis.ConnectionError as e:
            logging.warning(f"Redis not available at {self.host}:{self.port}: {e}")
            self.client = None
            self.pubsub = None

    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            return self.client is not None and self.client.ping() is not None
        except Exception:
            return False

    # ---------------- envelope helpers ----------------
    def _ensure_envelope(self, topic: str, message: Any) -> Dict[str, Any]:
        if isinstance(message, dict) and 'buzz' in message:
            buzz = message['buzz']
            if 'id' not in buzz:
                buzz['id'] = str(uuid.uuid4())
            if 'ts' not in buzz:
                buzz['ts'] = int(time.time() * 1000)
            if 'type' not in buzz:
                buzz['type'] = topic
            if 'source' not in buzz:
                buzz['source'] = 'UNKNOWN'
            return message
        # wrap
        return {'buzz': {'id': str(uuid.uuid4()), 'type': topic, 'source': 'UNKNOWN', 'ts': int(time.time() * 1000)}, 'payload': message}

    def publish(self, channel: str, message: Any):
        """Publish a buzz message to a Redis Stream (preferred) or PUB/SUB fallback.

        `channel` is used as stream name for XADD. Message will be JSON-serialized.
        """
        msg = self._ensure_envelope(channel, message)
        try:
            data = json.dumps(msg, default=str)
        except Exception:
            data = json.dumps({'buzz': {'type': channel, 'ts': int(time.time()*1000)}, 'payload': str(message)})

        if not self.is_connected():
            logging.warning("Redis not connected, cannot publish to streams; attempting PUB/SUB fallback")
            try:
                if getattr(self, 'pubsub', None):
                    self.client.publish(channel, data)
                return
            except Exception:
                return

        try:
            # XADD to stream
            stream = channel
            self.client.xadd(stream, {'data': data})
            # also cache latest value for quick access
            try:
                self.client.set(f"cache:{channel}", data, ex=30)
            except Exception:
                pass
            logging.debug(f"XADD {stream}: {data}")
        except Exception as e:
            logging.exception(f"Error xadd to {channel}: {e}")

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None], group: Optional[str] = None):
        """Subscribe to a Redis Stream topic using a consumer group.

        Handler is called with the deserialized buzz message.
        """
        if not self.is_connected():
            logging.warning("Redis not connected, cannot subscribe to streams")
            return

        group = group or f"{self.consumer_group_pref}:{topic}"
        consumer_name = f"consumer-{uuid.uuid4().hex[:8]}"
        stream = topic

        try:
            # create group if not exists
            try:
                self.client.xgroup_create(stream, group, id='$', mkstream=True)
            except redis.ResponseError:
                # group exists
                pass
        except Exception:
            logging.exception(f"Failed to ensure consumer group for {stream}")

        def _loop():
            while not self._stop.is_set():
                try:
                    resp = self.client.xreadgroup(groupname=group, consumername=consumer_name, streams={stream: '>'}, count=10, block=1000)
                    if not resp:
                        continue
                    for s, messages in resp:
                        for msg_id, fields in messages:
                            raw = fields.get('data') or fields.get('message')
                            if not raw:
                                # ack and continue to avoid stuck
                                try:
                                    self.client.xack(stream, group, msg_id)
                                except Exception:
                                    pass
                                continue
                            try:
                                evt = json.loads(raw)
                            except Exception:
                                logging.exception('Failed to parse stream message')
                                try:
                                    self.client.xack(stream, group, msg_id)
                                except Exception:
                                    pass
                                continue

                            # dedupe by buzz.id
                            buzz = evt.get('buzz', {})
                            bid = buzz.get('id')
                            if bid:
                                if bid in self._seen:
                                    # already processed
                                    try:
                                        self.client.xack(stream, group, msg_id)
                                    except Exception:
                                        pass
                                    continue
                                # mark seen
                                self._seen[bid] = time.time()
                                if len(self._seen) > self._seen_max:
                                    # pop oldest
                                    self._seen.popitem(last=False)

                            # call handler
                            try:
                                handler(evt)
                            except Exception:
                                logging.exception('Subscriber handler failed')
                            finally:
                                try:
                                    self.client.xack(stream, group, msg_id)
                                except Exception:
                                    pass
                except Exception:
                    logging.exception('Stream consumer error')
                    time.sleep(1)

        t = threading.Thread(target=_loop, daemon=True)
        t.start()
        self._subs_threads.append(t)
        self._consumers[topic].append((group, consumer_name))
        logging.info(f"Subscribed to stream {topic} as {consumer_name} in group {group}")

    def set_cache(self, key: str, value: Any, expire: Optional[int] = None):
        """Set a cached value."""
        if not self.is_connected():
            logging.warning("Redis not connected, cannot cache")
            return
        try:
            data = json.dumps(value) if not isinstance(value, str) else value
            self.client.set(key, data, ex=expire)
            logging.debug(f"Cached {key}: {data}")
        except Exception as e:
            logging.error(f"Error caching {key}: {e}")

    def get_cache(self, key: str) -> Optional[Any]:
        """Get a cached value."""
        if not self.is_connected():
            logging.warning("Redis not connected, cannot get cache")
            return None
        try:
            data = self.client.get(key)
            if data:
                try:
                    return json.loads(data)
                except Exception:
                    return data
            return None
        except Exception as e:
            logging.error(f"Error getting cache {key}: {e}")
            return None

    def delete_cache(self, key: str):
        """Delete a cached value."""
        if not self.is_connected():
            return
        try:
            self.client.delete(key)
            logging.debug(f"Deleted cache {key}")
        except Exception as e:
            logging.error(f"Error deleting cache {key}: {e}")

    def listen(self):
        """Listen for messages (call in a thread)."""
        if not self.pubsub:
            return
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                # Handled by callback
                pass

    def share_data(self, key: str, data: Any):
        """Share data via cache and publish update."""
        # cache the raw value for quick access
        try:
            self.set_cache(f"cache:{key}", data, expire=60)
        except Exception:
            pass
        # publish on the named stream so subscribers can read
        try:
            self.publish(key, data)
        except Exception:
            logging.exception('share_data publish failed')

    def get_shared_data(self, key: str) -> Optional[Any]:
        """Get shared data from cache."""
        return self.get_cache(f"cache:{key}")

    def close(self):
        """Close connections."""
        if self.pubsub:
            self.pubsub.close()
        if self.client:
            self.client.close()
        logging.info("Network Agent connections closed")
        # stop subscriber threads
        try:
            self._stop.set()
            for t in self._subs_threads:
                if t.is_alive():
                    t.join(timeout=1)
        except Exception:
            pass

    def _health_loop(self):
        while True:
            try:
                self.publish_health()
            except Exception:
                logging.exception('health loop failed')
            time.sleep(self._health_interval)

    def publish_health(self):
        """Publish a simple health summary about the bus and topic lags."""
        info = {'bus': 'redis_streams', 'state': 'UNKNOWN', 'topics': {}}
        try:
            if not self.is_connected():
                info['state'] = 'DOWN'
            else:
                info['state'] = 'OK'
                # compute lag (pending) for tracked consumers
                for topic, consumers in self._consumers.items():
                    try:
                        pending = 0
                        # sum pending for groups related to topic
                        for group, _ in consumers:
                            try:
                                pend = self.client.xpending(topic, group)
                                # xpending returns a dict-like in redis-py; attempt to extract count
                                if isinstance(pend, dict) and 'pending' in pend:
                                    pending += int(pend.get('pending', 0))
                                elif isinstance(pend, int):
                                    pending += pend
                            except Exception:
                                # fallback: skip
                                pass
                        info['topics'][topic] = {'pending': pending}
                    except Exception:
                        info['topics'][topic] = {'pending': None}
        except Exception:
            logging.exception('publish_health failed')
        evt = {'buzz': {'type': 'buzz.net.health', 'source': 'NETWORK', 'ts': int(time.time()*1000)}, 'payload': info}
        try:
            # publish health to its own stream
            if self.is_connected():
                self.publish('buzz.net.health', evt)
            else:
                logging.info('Network health: %s', info)
        except Exception:
            logging.exception('Failed to emit network health')