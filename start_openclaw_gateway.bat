@echo off
REM OpenClaw Gateway Starter for LuciferOS
REM This script starts the OpenClaw gateway with Groq API key

cd /d C:\LuciferOS_FULL\openclaw

set GROQ_API_KEY=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

echo Starting OpenClaw Gateway...
echo Model: groq/llama-3.3-70b-versatile
echo Port: 19002

node openclaw.mjs gateway --port 19002
