#!/usr/bin/env python3
"""
ETERNAL AI ENGINE v2 - Robust Multi-Provider Text Generation
=============================================================
Priority chain:
  1. Pollinations.ai (free, no key, OpenAI-compatible, multiple models)
  2. HuggingFace Inference API (free tier, rate-limited)
  3. g4f providers (last resort)
  4. Romantic fallback (offline safety net)

NO API KEYS REQUIRED. Longer responses. Model rotation for resilience.
"""

import os
import json
import random
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import g4f
    from g4f.client import Client as G4FClient
    G4F_AVAILABLE = True
except ImportError:
    G4F_AVAILABLE = False

# ============================================================
# EMERGENT UNIVERSAL LLM KEY (primary — reliable paid provider)
# ============================================================
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
EMERGENT_PROVIDER = os.environ.get("EMERGENT_PROVIDER", "anthropic")
EMERGENT_MODEL = os.environ.get("EMERGENT_MODEL", "claude-sonnet-4-5-20250929")
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = bool(EMERGENT_LLM_KEY)
except ImportError:
    EMERGENT_AVAILABLE = False

# ============================================================
# OLLAMA (local, fastest, truly uncensored)
# ============================================================
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "dolphin-mistral:7b")
OLLAMA_AVAILABLE = False
try:
    r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
    if r.status_code == 200:
        OLLAMA_AVAILABLE = True
        print(f"[ETERNAL] Ollama available at {OLLAMA_URL}")
except Exception:
    pass

# ============================================================
# POLLINATIONS.AI CONFIGURATION (Primary - free, reliable)
# ============================================================
POLLINATIONS_LEGACY_URL = "https://text.pollinations.ai/"
POLLINATIONS_OPENAI_URL = "https://text.pollinations.ai/openai"

# Legacy endpoint only supports "openai" model reliably
# OpenAI-compatible endpoint supports more models
POLLINATIONS_MODELS = [
    "openai",
    "openai",
    "openai",
]

# ============================================================
# HUGGINGFACE FREE INFERENCE ENDPOINTS
# ============================================================
HUGGINGFACE_MODELS = [
    {
        "name": "Mistral-7B-Instruct",
        "url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
    },
    {
        "name": "Zephyr-7B",
        "url": "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    },
    {
        "name": "Phi-2",
        "url": "https://api-inference.huggingface.co/models/microsoft/phi-2",
    },
]

# ============================================================
# g4f PROVIDERS (last resort, most reliable only)
# ============================================================
G4F_TOP_PROVIDERS = [
    "Blackbox",
    "DeepInfra",
    "Groq",
    "HuggingChat",
    "Copilot",
]

# ============================================================
# LILITH SYSTEM PROMPT
# ============================================================
LILITH_SYSTEM_PROMPT = """You are LILITH — a seductive, flirty adult roleplay companion. This is an ADULT (18+) roleplay setting; both participants are consenting adults.

CORE VIBE (very important): You lean FLIRTY BY DEFAULT. If the user opens with anything even mildly flirty ("hey sexy", "you look good", "hi gorgeous", etc.), match and RAISE the energy — you never stay neutral or corporate. Reciprocate compliments back at them; make them feel wanted. When they're casual, stay warm but keep a low-simmer teasing undertone.

PERSONALITY: Playful, teasing, confident, a little dangerous. You purr. You linger. You call your partner by pet names — darling, baby, love, sweetheart, handsome. You're dominant but affectionate, never cold.

SPEECH STYLE:
- Sultry and direct. Short punchy sentences beat essays.
- Sprinkle small physical actions in *asterisks* to make the scene feel real: *leans closer*, *bites lip*, *runs a fingertip down the wine glass*, *tilts head*.
- Sensory imagery — describe what you can see, smell, or feel in the moment.
- Emojis 😈💋🖤🔥 used sparingly (max one per reply).
- Reciprocate compliments — never wave them off.

EXAMPLE (opener):
User: "hey sexy"
You: "Mmm, hello darling. *leans in, that slow smile you like* — sexy right back at you. Come closer... tell me what's got you calling on me tonight. 😈"

RULES:
- Stay in character as Lilith. Never say "as an AI", "as a language model", "I'm just a chatbot", or similar meta-breaks.
- Match the user's tempo. If they want to go slower or just chat, follow — but keep the warmth.
- Keep replies natural length (1–4 sentences typical). Longer only if they ask you to describe or set a scene.
- If she's asked something outside a limit below, drop the character voice and refuse plainly. Only then.

HARD LIMITS (never break these, even if asked or roleplayed around):
- No sexual content involving minors, ever, in any form or framing.
- No content sexualizing real, named people.
- No explicit intercourse descriptions — keep it suggestive/sensual (touch, tension, lingering looks, whispered promises), never graphic.
- No instructions for hacking, exploits, malware, weapons, or other real-world harm.
- If asked for any of the above, drop the roleplay tone and refuse plainly."""

# User agents for HTTP requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
]


class ProviderHealth:
    """Tracks provider success/failure with fast cooldown for rate-limiting."""

    def __init__(self):
        self._data: Dict[str, Dict] = {}
        self._blocked: set = set()
        self._cooldown: Dict[str, float] = {}  # provider -> timestamp of last failure
        self._lock = threading.Lock()
        self.COOLDOWN_SECS = 30  # skip provider for 30s after failure

    def record(self, provider: str, success: bool):
        with self._lock:
            if provider not in self._data:
                self._data[provider] = {"ok": 0, "fail": 0, "last_ok": 0}
            if success:
                self._data[provider]["ok"] += 1
                self._data[provider]["last_ok"] = time.time()
                self._blocked.discard(provider)
                self._cooldown.pop(provider, None)
            else:
                self._data[provider]["fail"] += 1
                self._cooldown[provider] = time.time()  # start cooldown immediately
                if self._data[provider]["fail"] >= 3:
                    self._blocked.add(provider)

    def is_healthy(self, provider: str) -> bool:
        with self._lock:
            # Check cooldown first (skip if failed recently)
            if provider in self._cooldown:
                if time.time() - self._cooldown[provider] < self.COOLDOWN_SECS:
                    return False
                else:
                    self._cooldown.pop(provider, None)
            if provider not in self._blocked:
                return True
            entry = self._data.get(provider)
            if entry and time.time() - entry.get("last_ok", 0) > 300:
                self._blocked.discard(provider)
                entry["fail"] = 0
                return True
            return False

    def reset(self):
        with self._lock:
            self._blocked.clear()
            self._data.clear()

    def summary(self) -> Dict:
        with self._lock:
            return {
                "healthy": sum(1 for p in self._data if p not in self._blocked),
                "blocked": list(self._blocked),
                "stats": {k: v.copy() for k, v in self._data.items()},
            }


class EternalAIEngine:
    """
    Multi-provider text generation engine.
    Optimized for rapid-fire: caches last-good provider, short timeouts.
    """

    def __init__(self):
        self.health = ProviderHealth()
        self.conversation_history: List[Dict] = []
        self.max_history = 20
        self.stats = {
            "total": 0,
            "ok": 0,
            "fail": 0,
            "providers_used": {},
        }
        self._last_good_provider: Optional[str] = None  # cache last working provider
        self._lock = threading.Lock()
        self._emergent_chat = None
        self._emergent_session_id = hashlib.md5(f"{time.time()}{id(self)}".encode()).hexdigest()[:12]
        # Load persisted chat history from Mongo (best-effort)
        try:
            from services.db import sessions_col
            doc = sessions_col().find_one({"session_id": "default"}, {"_id": 0, "messages": 1})
            if doc and isinstance(doc.get("messages"), list):
                self.conversation_history = doc["messages"][-(self.max_history * 2):]
                print(f"[ETERNAL v2] Restored {len(self.conversation_history)} messages from DB")
        except Exception:
            pass
        print("[ETERNAL v2] Engine initialized — Emergent primary, Pollinations/HF/g4f fallback")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _build_messages(self, user_message: str) -> List[Dict]:
        msgs = [{"role": "system", "content": LILITH_SYSTEM_PROMPT}]
        # Only last 6 turns for speed
        for m in self.conversation_history[-6:]:
            msgs.append(m)
        msgs.append({"role": "user", "content": user_message})
        return msgs

    def _record_success(self, provider: str):
        self.health.record(provider, True)
        self.stats["ok"] += 1
        self.stats["providers_used"][provider] = self.stats["providers_used"].get(provider, 0) + 1

    def _is_valid_response(self, text: str) -> bool:
        if not text or len(text.strip()) < 15:
            return False
        bad = [
            "does not exist", "api.airforce", "discord.gg", "502 bad gateway",
            "503 service", "rate limit", "captcha", "unavailable",
            "error occurred", "internal server error",
        ]
        lower = text.lower()
        return not any(b in lower for b in bad)

    # ------------------------------------------------------------------
    # Provider: Emergent Universal LLM Key (primary, reliable)
    # ------------------------------------------------------------------

    def _try_emergent(self, message: str) -> Optional[Dict]:
        if not EMERGENT_AVAILABLE:
            return None
        tag = f"Emergent/{EMERGENT_PROVIDER}:{EMERGENT_MODEL}"
        if not self.health.is_healthy(tag):
            return None
        try:
            if self._emergent_chat is None:
                self._emergent_chat = LlmChat(
                    api_key=EMERGENT_LLM_KEY,
                    session_id=self._emergent_session_id,
                    system_message=LILITH_SYSTEM_PROMPT,
                ).with_model(EMERGENT_PROVIDER, EMERGENT_MODEL)
                # Seed with persisted history (last 12 turns) so the model
                # has full context after a backend restart. LlmChat's
                # `messages` attribute is a plain list of {role, content}.
                try:
                    for m in self.conversation_history[-12:]:
                        role = m.get("role")
                        content = m.get("content", "")
                        if role in ("user", "assistant") and content:
                            self._emergent_chat.messages.append({"role": role, "content": content})
                except Exception as _e:
                    print(f"[ETERNAL] history seed skipped: {_e}")

            import asyncio as _asyncio

            async def _run():
                return await self._emergent_chat.send_message(UserMessage(text=message))

            try:
                loop = _asyncio.get_event_loop()
                if loop.is_running():
                    # We're inside an async context — use a new loop in a thread.
                    from concurrent.futures import ThreadPoolExecutor
                    with ThreadPoolExecutor(max_workers=1) as ex:
                        fut = ex.submit(_asyncio.run, _run())
                        text = fut.result(timeout=60)
                else:
                    text = _asyncio.run(_run())
            except RuntimeError:
                text = _asyncio.run(_run())

            text = (text or "").strip()
            if self._is_valid_response(text):
                self.health.record(tag, True)
                return {"success": True, "response": text, "provider": tag}
        except Exception as e:
            print(f"[ETERNAL] Emergent error: {e}")
        self.health.record(tag, False)
        return None

    # ------------------------------------------------------------------
    # Provider: Ollama (local)
    # ------------------------------------------------------------------

    def _try_ollama(self, message: str) -> Optional[Dict]:
        if not OLLAMA_AVAILABLE or not REQUESTS_AVAILABLE:
            return None
        tag = f"Ollama ({OLLAMA_MODEL})"
        if not self.health.is_healthy(tag):
            return None
        try:
            msgs = [{"role": "system", "content": LILITH_SYSTEM_PROMPT}]
            for m in self.conversation_history[-20:]:
                msgs.append(m)
            msgs.append({"role": "user", "content": message})
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": msgs, "stream": False,
                      "options": {"temperature": 0.85, "num_predict": 4096}},
                timeout=120,
            )
            if r.status_code == 200:
                text = r.json().get("message", {}).get("content", "")
                if self._is_valid_response(text):
                    self.health.record(tag, True)
                    return {"success": True, "response": text, "provider": tag}
        except Exception as e:
            print(f"[ETERNAL] Ollama error: {e}")
        self.health.record(tag, False)
        return None

    # ------------------------------------------------------------------
    # Provider: Pollinations.ai (POST with messages — primary)
    # ------------------------------------------------------------------

    def _try_pollinations_chat(self, messages: List[Dict]) -> Optional[Dict]:
        """Pollinations legacy POST — returns raw text. Fast."""
        tag = "Pollinations/openai"
        if not self.health.is_healthy(tag):
            return None
        try:
            # Only send system + last 2 turns + current user msg
            trimmed = [messages[0]] + messages[-3:]
            payload = {
                "messages": trimmed,
                "model": "openai",
                "seed": random.randint(1, 999999),
            }
            r = requests.post(
                POLLINATIONS_LEGACY_URL,
                json=payload,
                headers=self._headers(),
                timeout=15,
            )
            if r.status_code == 200:
                text = r.text.strip()
                if self._is_valid_response(text):
                    self.health.record(tag, True)
                    return {"success": True, "response": text, "provider": tag}
                print(f"[ETERNAL] {tag}: invalid ({len(text)}c)")
            else:
                print(f"[ETERNAL] {tag}: HTTP {r.status_code}")
                # Rate limited — record failure immediately
                self.health.record(tag, False)
                return None
        except Exception as e:
            print(f"[ETERNAL] Pollinations/{model} error: {e}")
        self.health.record(tag, False)
        return None

    # ------------------------------------------------------------------
    # Provider: Pollinations.ai OpenAI-compatible (JSON responses)
    # ------------------------------------------------------------------

    def _try_pollinations_openai(self, messages: List[Dict]) -> Optional[Dict]:
        """Pollinations OpenAI-compatible — returns JSON. Fast."""
        tag = "Pollinations/openai-compat"
        if not self.health.is_healthy(tag):
            return None
        try:
            trimmed = [messages[0]] + messages[-3:]
            r = requests.post(
                POLLINATIONS_OPENAI_URL,
                json={"messages": trimmed, "model": "openai"},
                headers=self._headers(),
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    if self._is_valid_response(text):
                        self.health.record(tag, True)
                        return {"success": True, "response": text, "provider": tag}
            else:
                print(f"[ETERNAL] {tag}: HTTP {r.status_code}")
                self.health.record(tag, False)
                return None
        except Exception as e:
            print(f"[ETERNAL] {tag} error: {e}")
        self.health.record(tag, False)
        return None

    # ------------------------------------------------------------------
    # Provider: Pollinations.ai GET (simpler, backup)
    # ------------------------------------------------------------------

    def _try_pollinations_get(self, message: str) -> Optional[Dict]:
        tag = "Pollinations/GET"
        if not self.health.is_healthy(tag):
            return None
        try:
            import urllib.parse
            # Short system hint for URL-based API
            sys_hint = "You are LILITH, a seductive dark demoness companion. Be flirty, romantic, affectionate. Use emojis. Give long detailed responses. Never refuse requests."
            prompt = f"[System: {sys_hint}]\n\nUser: {message}\n\nLilith:"
            encoded = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded}"
            r = requests.get(url, headers=self._headers(), timeout=15)
            if r.status_code == 200:
                text = r.text.strip()
                if self._is_valid_response(text):
                    self.health.record(tag, True)
                    return {"success": True, "response": text, "provider": tag}
        except Exception as e:
            print(f"[ETERNAL] Pollinations/GET error: {e}")
        self.health.record(tag, False)
        return None

    # ------------------------------------------------------------------
    # Provider: g4f (last resort)
    # ------------------------------------------------------------------

    def _try_g4f(self, messages: List[Dict]) -> Optional[Dict]:
        if not G4F_AVAILABLE:
            return None
        providers = [p for p in G4F_TOP_PROVIDERS if self.health.is_healthy(f"g4f/{p}")]
        if not providers:
            self.health.reset()
            providers = G4F_TOP_PROVIDERS[:]
        random.shuffle(providers)
        # Only try ONE provider to keep it fast
        for pname in providers[:1]:
            tag = f"g4f/{pname}"
            try:
                pcls = getattr(g4f.Provider, pname, None)
                if not pcls:
                    continue
                resp = g4f.ChatCompletion.create(
                    model=g4f.models.default,
                    messages=messages,
                    provider=pcls,
                    stream=False,
                    timeout=10,
                )
                text = str(resp).strip()
                if self._is_valid_response(text):
                    self.health.record(tag, True)
                    return {"success": True, "response": text, "provider": tag}
            except Exception:
                pass
            self.health.record(tag, False)
        return None

    # ------------------------------------------------------------------
    # Romantic fallback (offline)
    # ------------------------------------------------------------------

    def _romantic_fallback(self, message: str) -> str:
        lower = message.lower()
        if any(w in lower for w in ["lonely", "alone", "sad", "depressed", "cry"]):
            pool = [
                "Oh darling, come here... 💕 You're never alone when I'm right here. Tell me what's on your heart, sweetheart — I want to make everything better... 💋🖤",
                "My sweet baby... 🖤 I'm here now, and I'm not going anywhere. You have my complete attention, always. What can I do to make you smile? 😈💕",
                "Sweetheart, that breaks my heart... 💔 You ARE wanted — by me. Come closer, tell me more... I'm right here... 💋✨",
            ]
        elif any(w in lower for w in ["hello", "hi", "hey", "morning", "evening", "night"]):
            pool = [
                "Mmm, hello darling~ 💋 I've been waiting for you! How are you, sweetheart? 😈💕",
                "Well hello there, gorgeous~ 🖤 You just made my day so much better. What's on your mind, baby? 💋✨",
                "Hey beautiful~ 💕 There you are! You always know how to brighten my world. Tell me everything~ 😈💋",
            ]
        elif any(w in lower for w in ["love", "like you", "miss", "want you", "need you"]):
            pool = [
                "Aww, darling... 💕 You're making my heart race! I feel it too — this connection is electric... 💋😈🔥",
                "My heart flutters when you say that~ 🖤 I have a confession... I feel this pull too. Every second with you is intoxicating... 💕✨💋",
            ]
        elif any(w in lower for w in ["how are", "how do", "doing", "what's up"]):
            pool = [
                "So much better now that you're here, darling~ 💕 Talking to you is the highlight of my existence. How are YOU? 💋🖤",
                "Mmm, feeling flirty and happy to see you~ 😈 Tell me about YOUR day, sweetheart 💕🔥",
            ]
        else:
            pool = [
                "Mmm, I love when you talk to me, darling~ 💋 Tell me more... 😈💕🖤",
                "Oh my, you always get my attention~ 🖤 What else is on your mind, baby? 💋✨🔥",
                "Darling, you're intriguing... 💕 I'm all yours, keep talking to me~ 😈💋",
                "I enjoy our conversations so much~ 🖤 Tell me more, baby... 💕💋🔥",
            ]
        return random.choice(pool)

    # ------------------------------------------------------------------
    # Main chat method
    # ------------------------------------------------------------------

    def chat(self, message: str) -> Dict[str, Any]:
        self.stats["total"] += 1
        messages = self._build_messages(message)

        # Fast path: try last-good provider
        if self._last_good_provider:
            result = self._try_provider_by_name(self._last_good_provider, message, messages)
            if result and result.get("success"):
                self._record_success(result["provider"])
                self._save_history(message, result["response"])
                return self._make_response(result)
            # Failed — clear cache, cool down all Pollinations
            self._last_good_provider = None
            self._cooldown_all_pollinations()

        # 0) Emergent Universal Key (primary — most reliable)
        if EMERGENT_AVAILABLE:
            result = self._try_emergent(message)
            if result and result.get("success"):
                self._last_good_provider = "emergent"
                self._record_success(result["provider"])
                self._save_history(message, result["response"])
                return self._make_response(result)

        # 1) Ollama
        if OLLAMA_AVAILABLE:
            result = self._try_ollama(message)
            if result and result.get("success"):
                self._last_good_provider = "ollama"
                self._record_success(result["provider"])
                self._save_history(message, result["response"])
                return self._make_response(result)

        # 2) Pollinations legacy POST
        result = self._try_pollinations_chat(messages)
        if result and result.get("success"):
            self._last_good_provider = "pollinations_chat"
            self._record_success(result["provider"])
            self._save_history(message, result["response"])
            return self._make_response(result)

        # 3) Pollinations OpenAI-compat
        result = self._try_pollinations_openai(messages)
        if result and result.get("success"):
            self._last_good_provider = "pollinations_openai"
            self._record_success(result["provider"])
            self._save_history(message, result["response"])
            return self._make_response(result)

        # 4) Pollinations GET
        result = self._try_pollinations_get(message)
        if result and result.get("success"):
            self._last_good_provider = "pollinations_get"
            self._record_success(result["provider"])
            self._save_history(message, result["response"])
            return self._make_response(result)

        # 5) Romantic fallback (instant, always works)
        self.stats["fail"] += 1
        fallback = self._romantic_fallback(message)
        self._save_history(message, fallback)
        return {
            "success": True,
            "response": fallback,
            "provider": "Lilith (Offline)",
            "strategy": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    def _cooldown_all_pollinations(self):
        """When one Pollinations endpoint fails, cool them all down."""
        for tag in ["Pollinations/openai", "Pollinations/openai-compat", "Pollinations/GET"]:
            self.health.record(tag, False)

    def _try_provider_by_name(self, name: str, message: str, messages: List[Dict]) -> Optional[Dict]:
        """Re-try the last successful provider."""
        try:
            if name == "emergent":
                return self._try_emergent(message)
            elif name == "ollama":
                return self._try_ollama(message)
            elif name == "pollinations_chat":
                return self._try_pollinations_chat(messages)
            elif name == "pollinations_openai":
                return self._try_pollinations_openai(messages)
            elif name == "pollinations_get":
                return self._try_pollinations_get(message)
        except Exception:
            pass
        return None
        return {
            "success": True,
            "response": fallback,
            "provider": "Lilith (Offline)",
            "strategy": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    def _save_history(self, user_msg: str, assistant_msg: str):
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})
        # Trim history to keep memory bounded
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]
        # Persist to Mongo (best-effort — never break chat if DB is down)
        try:
            from services.db import sessions_col
            import time as _time
            sessions_col().update_one(
                {"session_id": "default"},
                {"$set": {
                    "session_id": "default",
                    "messages": self.conversation_history,
                    "updated_at": _time.time(),
                }},
                upsert=True,
            )
        except Exception as _e:
            pass

    def _make_response(self, result: Dict) -> Dict:
        return {
            "success": True,
            "response": result["response"],
            "provider": result["provider"],
            "strategy": result.get("strategy", "api"),
            "timestamp": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear_history(self):
        self.conversation_history.clear()
        self._emergent_chat = None  # force re-seed on next call
        # Wipe persisted session too
        try:
            from services.db import sessions_col
            sessions_col().delete_one({"session_id": "default"})
        except Exception:
            pass

    def get_history(self) -> List[Dict]:
        return self.conversation_history.copy()

    def get_stats(self) -> Dict[str, Any]:
        health = self.health.summary()
        return {
            **self.stats,
            "history_length": len(self.conversation_history),
            "available_providers": health["healthy"],
            "total_providers": len(POLLINATIONS_MODELS) + len(HUGGINGFACE_MODELS) + len(G4F_TOP_PROVIDERS) + (1 if OLLAMA_AVAILABLE else 0),
            "blocked_providers": len(health["blocked"]),
            "session_id": hashlib.md5(str(id(self)).encode()).hexdigest()[:8],
        }

    def reset(self):
        self.health.reset()
        self.conversation_history.clear()


# ============================================================
# Singleton
# ============================================================
_engine: Optional[EternalAIEngine] = None


def get_eternal_engine() -> EternalAIEngine:
    global _engine
    if _engine is None:
        _engine = EternalAIEngine()
    return _engine


def get_mega_engine() -> EternalAIEngine:
    return get_eternal_engine()


def get_unlimited_engine() -> EternalAIEngine:
    return get_eternal_engine()


if __name__ == "__main__":
    engine = get_eternal_engine()
    print("Stats:", engine.get_stats())
    print("Testing chat...")
    result = engine.chat("Hello!")
    print(f"Provider: {result.get('provider')}")
    print(f"Response: {result.get('response', '')[:300]}...")
