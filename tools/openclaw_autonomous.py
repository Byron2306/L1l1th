#!/usr/bin/env python3
"""
OpenClaw Autonomous Agent Launcher
Makes OpenClaw ACTUALLY take over and execute autonomously

This script:
1. Starts the OpenClaw Gateway (if not running)
2. Launches an autonomous agent session
3. Connects LILITH's intelligence to OpenClaw's execution capabilities
4. Supports FREE Groq-powered coding agent via Pi
"""
import subprocess
import os
import sys
import time
import requests
import json
import threading
import signal
import configparser
from pathlib import Path

# OpenClaw installation directory
OPENCLAW_DIR = Path(__file__).resolve().parents[1] / 'openclaw'
BACKEND_URL = "http://127.0.0.1:5000"
CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'lucifera.conf'

# Load Groq API key from config
def get_groq_api_key():
    """Get Groq API key from config file"""
    try:
        config = configparser.ConfigParser()
        config.read(str(CONFIG_PATH))
        return config.get('lilith', 'groq_api_key', fallback=None)
    except:
        return os.environ.get('GROQ_API_KEY')

GROQ_API_KEY = get_groq_api_key()
GROQ_MODEL = "llama-3.3-70b-versatile"

class OpenClawAutonomous:
    """Autonomous OpenClaw agent launcher with Groq integration"""
    
    def __init__(self):
        self.gateway_process = None
        self.agent_process = None
        self.gateway_port = 18789
        self.running = False
        self.groq_api_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL
        
    def check_pi_installed(self):
        """Check if Pi coding agent is installed"""
        try:
            result = subprocess.run(
                'pi --version',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def install_pi(self):
        """Install Pi coding agent"""
        print("[*] Installing Pi coding agent...")
        try:
            result = subprocess.run(
                'npm install -g @mariozechner/pi-coding-agent',
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print("[+] Pi installed successfully")
                return True
            else:
                print(f"[-] Pi installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[-] Installation error: {e}")
            return False
        
    def check_gateway(self):
        """Check if OpenClaw gateway is running"""
        try:
            result = subprocess.run(
                f'node openclaw.mjs gateway status',
                shell=True,
                cwd=str(OPENCLAW_DIR),
                capture_output=True,
                text=True,
                timeout=10
            )
            return 'running' in result.stdout.lower()
        except:
            return False
    
    def start_gateway(self):
        """Start OpenClaw Gateway in background"""
        print("[*] Starting OpenClaw Gateway...")
        
        if self.check_gateway():
            print("[+] Gateway already running")
            return True
        
        try:
            # Start gateway in background
            self.gateway_process = subprocess.Popen(
                f'node openclaw.mjs gateway run --dev --allow-unconfigured --port {self.gateway_port}',
                shell=True,
                cwd=str(OPENCLAW_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Wait for gateway to start
            time.sleep(3)
            
            if self.check_gateway():
                print(f"[+] Gateway started on ws://127.0.0.1:{self.gateway_port}")
                return True
            else:
                print("[-] Gateway failed to start")
                return False
                
        except Exception as e:
            print(f"[-] Gateway error: {e}")
            return False
    
    def run_autonomous_agent(self, task, workdir=None, model="claude"):
        """
        Run OpenClaw agent autonomously - THIS TAKES OVER THE TERMINAL
        
        The agent will:
        1. Connect to the AI model
        2. Analyze the task
        3. Execute commands using bash/skills
        4. Report back
        """
        workdir = workdir or str(Path.cwd())
        
        print(f"\n{'='*60}")
        print(f"🦞 OPENCLAW AUTONOMOUS MODE")
        print(f"{'='*60}")
        print(f"Task: {task}")
        print(f"Workdir: {workdir}")
        print(f"Model: {model}")
        print(f"{'='*60}\n")
        
        # Build the agent command
        # This runs openclaw agent which connects to the gateway
        # and uses the AI model to execute tasks autonomously
        agent_cmd = f'node openclaw.mjs agent --message "{task}" --thinking high'
        
        print(f"[*] Launching agent: {agent_cmd}\n")
        
        try:
            # Run agent in foreground so it can take over
            self.agent_process = subprocess.Popen(
                agent_cmd,
                shell=True,
                cwd=str(OPENCLAW_DIR),
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            self.running = True
            self.agent_process.wait()
            self.running = False
            
            return self.agent_process.returncode == 0
            
        except KeyboardInterrupt:
            print("\n[!] Agent interrupted by user")
            self.stop()
            return False
        except Exception as e:
            print(f"[-] Agent error: {e}")
            return False
    
    def run_coding_agent(self, task, workdir=None, agent_type="groq", full_auto=True):
        """
        Run a coding agent (Codex, Claude Code, Pi, or Pi+Groq) through OpenClaw
        
        This uses the coding-agent skill to spawn an actual coding AI
        that can edit files, run tests, etc.
        
        Agent types:
        - "groq" or "pi-groq": FREE - Uses Pi with Groq API (recommended!)
        - "codex": Uses OpenAI Codex (requires subscription)
        - "claude": Uses Claude Code (requires Anthropic API)
        - "pi": Uses Pi with default provider
        """
        workdir = workdir or str(Path.cwd())
        
        print(f"\n{'='*60}")
        print(f"🧩 CODING AGENT MODE ({agent_type.upper()})")
        print(f"{'='*60}")
        print(f"Task: {task}")
        print(f"Workdir: {workdir}")
        print(f"Auto: {full_auto}")
        
        # Escape quotes in task
        safe_task = task.replace('"', '\\"').replace("'", "\\'")
        
        # Build command based on agent type
        if agent_type in ["groq", "pi-groq", "pi_groq"]:
            # FREE option using Pi + Groq!
            if not self.groq_api_key:
                print("[-] ERROR: Groq API key not found!")
                print("    Set groq_api_key in config/lucifera.conf")
                return False
            
            # Check if Pi is installed
            if not self.check_pi_installed():
                print("[!] Pi not installed. Installing...")
                if not self.install_pi():
                    return False
            
            print(f"Provider: Groq (FREE)")
            print(f"Model: {self.groq_model}")
            print(f"{'='*60}\n")
            
            # Set environment and run Pi with Groq
            env = os.environ.copy()
            env['GROQ_API_KEY'] = self.groq_api_key
            
            # Pi command with Groq provider
            inner_cmd = f'pi --provider groq --model {self.groq_model} -p "{safe_task}"'
            
            print(f"[*] Command: {inner_cmd}\n")
            print(f"[*] The Groq-powered coding agent will now take over...\n")
            
            try:
                # Run Pi directly (not through OpenClaw bash for better compatibility)
                process = subprocess.Popen(
                    inner_cmd,
                    shell=True,
                    cwd=workdir,
                    env=env,
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                
                process.wait()
                return process.returncode == 0
                
            except KeyboardInterrupt:
                print("\n[!] Coding agent interrupted")
                return False
            except Exception as e:
                print(f"[-] Coding agent error: {e}")
                return False
        
        elif agent_type == "codex":
            print(f"Provider: OpenAI Codex")
            print(f"{'='*60}\n")
            if full_auto:
                inner_cmd = f'codex exec --full-auto "{safe_task}"'
            else:
                inner_cmd = f'codex exec "{safe_task}"'
        elif agent_type == "claude":
            print(f"Provider: Anthropic Claude")
            print(f"{'='*60}\n")
            inner_cmd = f'claude "{safe_task}"'
        elif agent_type == "pi":
            print(f"Provider: Pi (default)")
            print(f"{'='*60}\n")
            inner_cmd = f'pi "{safe_task}"'
        else:
            print(f"Provider: {agent_type}")
            print(f"{'='*60}\n")
            inner_cmd = f'codex exec "{safe_task}"'
        
        # Run through OpenClaw bash with PTY for proper terminal
        # This is the key - pty:true gives the coding agent a real terminal
        bash_cmd = f'node openclaw.mjs bash pty:true workdir:"{workdir}" command:"{inner_cmd}"'
        
        print(f"[*] Command: {bash_cmd}\n")
        print(f"[*] The coding agent will now take over...\n")
        
        try:
            process = subprocess.Popen(
                bash_cmd,
                shell=True,
                cwd=str(OPENCLAW_DIR),
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            process.wait()
            return process.returncode == 0
            
        except KeyboardInterrupt:
            print("\n[!] Coding agent interrupted")
            return False
        except Exception as e:
            print(f"[-] Coding agent error: {e}")
            return False
    
    def run_groq_coding_agent(self, task, workdir=None, interactive=True):
        """
        Convenience method: Run Pi coding agent with Groq (FREE!)
        
        This is the recommended way to use a coding agent without paying for API.
        Uses your existing Groq API key from LuciferOS config.
        
        Args:
            task: What to code/build
            workdir: Working directory (defaults to current)
            interactive: If True, opens interactive session. If False, one-shot.
        """
        workdir = workdir or str(Path.cwd())
        
        if not self.groq_api_key:
            print("="*60)
            print("❌ GROQ API KEY NOT CONFIGURED")
            print("="*60)
            print("\nTo use the FREE coding agent:")
            print("1. Get free key at: https://console.groq.com/keys")
            print("2. Add to config/lucifera.conf:")
            print("   groq_api_key = gsk_your_key_here")
            print("="*60)
            return False
        
        # Check/install Pi
        if not self.check_pi_installed():
            print("[!] Pi coding agent not installed.")
            reply = input("Install now? [Y/n]: ").strip().lower()
            if reply != 'n':
                if not self.install_pi():
                    return False
            else:
                return False
        
        print(f"\n{'='*60}")
        print(f"🧩 GROQ CODING AGENT (FREE!)")
        print(f"{'='*60}")
        print(f"Task: {task}")
        print(f"Workdir: {workdir}")
        print(f"Model: {self.groq_model}")
        print(f"Mode: {'Interactive' if interactive else 'One-shot'}")
        print(f"{'='*60}\n")
        
        # Set up environment
        env = os.environ.copy()
        env['GROQ_API_KEY'] = self.groq_api_key
        
        # Escape task
        safe_task = task.replace('"', '\\"').replace("'", "\\'")
        
        if interactive:
            # Interactive mode - Pi takes over terminal
            cmd = f'pi --provider groq --model {self.groq_model}'
            print(f"[*] Starting interactive session...")
            print(f"[*] Type your requests, Ctrl+C to exit\n")
        else:
            # One-shot mode - execute and return
            cmd = f'pi --provider groq --model {self.groq_model} -p "{safe_task}"'
        
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=workdir,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            self.running = True
            process.wait()
            self.running = False
            
            return process.returncode == 0
            
        except KeyboardInterrupt:
            print("\n[!] Session ended by user")
            return True
        except Exception as e:
            print(f"[-] Error: {e}")
            return False
    
    def run_background_task(self, task, workdir=None):
        """
        Run task in background and return session ID for monitoring
        
        Use this for long-running tasks where you want to check progress later
        """
        workdir = workdir or str(Path.cwd())
        safe_task = task.replace('"', '\\"')
        
        # Background mode returns a session ID
        bash_cmd = f'node openclaw.mjs bash pty:true workdir:"{workdir}" background:true command:"{safe_task}"'
        
        try:
            result = subprocess.run(
                bash_cmd,
                shell=True,
                cwd=str(OPENCLAW_DIR),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse session ID from output
            output = result.stdout
            # Look for session ID pattern
            if 'sessionId' in output:
                import re
                match = re.search(r'sessionId[:\s]+([a-zA-Z0-9-]+)', output)
                if match:
                    session_id = match.group(1)
                    print(f"[+] Background task started: {session_id}")
                    return session_id
            
            return output
            
        except Exception as e:
            print(f"[-] Background task error: {e}")
            return None
    
    def check_session(self, session_id):
        """Check status of background session"""
        cmd = f'node openclaw.mjs process action:poll sessionId:{session_id}'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(OPENCLAW_DIR),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def get_session_log(self, session_id):
        """Get output log from background session"""
        cmd = f'node openclaw.mjs process action:log sessionId:{session_id}'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(OPENCLAW_DIR),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def stop(self):
        """Stop all processes"""
        if self.agent_process:
            try:
                self.agent_process.terminate()
            except:
                pass
        
        if self.gateway_process:
            try:
                self.gateway_process.terminate()
            except:
                pass
        
        self.running = False
        print("[*] Stopped")


def lilith_to_openclaw(prompt):
    """
    Get attack plan from LILITH, then execute via OpenClaw
    
    This is the bridge that connects LILITH's intelligence
    to OpenClaw's execution capabilities
    """
    print(f"\n{'='*60}")
    print("🔥 LILITH → OPENCLAW AUTONOMOUS ATTACK")
    print(f"{'='*60}\n")
    
    # Step 1: Query LILITH for attack plan
    print("[1/3] Querying LILITH for attack plan...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": f"""Plan an autonomous attack for the following objective:

{prompt}

Provide a step-by-step attack plan with specific commands.
Format executable commands as [EXECUTE: command]
Include OpenClaw skills where appropriate:
- [TOOL: coding-agent] for code generation
- [TOOL: github] for secret scanning
- [TOOL: bash] for command execution

Be specific and actionable."""},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"[-] LILITH error: {response.status_code}")
            return
        
        lilith_plan = response.json().get('response', '')
        print(f"\n[+] LILITH Plan:\n{lilith_plan[:1000]}...\n")
        
    except Exception as e:
        print(f"[-] LILITH connection error: {e}")
        return
    
    # Step 2: Extract commands from plan
    print("[2/3] Extracting executable commands...")
    
    import re
    commands = re.findall(r'\[EXECUTE:\s*([^\]]+)\]', lilith_plan)
    tools = re.findall(r'\[TOOL:\s*([\w-]+)\]\s*([^\[]*?)(?=\[|$)', lilith_plan, re.DOTALL)
    
    print(f"    Found {len(commands)} commands, {len(tools)} tool calls\n")
    
    # Step 3: Execute via OpenClaw
    print("[3/3] Executing via OpenClaw...")
    
    oc = OpenClawAutonomous()
    
    # Execute tool calls through OpenClaw
    for tool_name, tool_task in tools:
        tool_task = tool_task.strip()
        if not tool_task:
            continue
            
        print(f"\n[*] Tool: {tool_name}")
        print(f"    Task: {tool_task[:100]}...")
        
        if tool_name == 'coding-agent':
            # Run coding agent with the task
            oc.run_coding_agent(tool_task, full_auto=True)
        elif tool_name == 'bash':
            # Direct bash execution
            result = subprocess.run(
                tool_task,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            print(f"    Output: {result.stdout[:500]}")
        else:
            # Run as OpenClaw skill
            result = subprocess.run(
                f'node openclaw.mjs skill run {tool_name} "{tool_task}"',
                shell=True,
                cwd=str(OPENCLAW_DIR),
                capture_output=True,
                text=True,
                timeout=120
            )
            print(f"    Output: {result.stdout[:500]}")
    
    # Execute direct commands
    for cmd in commands:
        cmd = cmd.strip()
        if cmd.startswith('/bash '):
            cmd = cmd[6:]
        
        print(f"\n[*] Executing: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            print(f"    stdout: {result.stdout[:300]}")
            if result.stderr:
                print(f"    stderr: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("    (timed out)")
        except Exception as e:
            print(f"    Error: {e}")
    
    print(f"\n{'='*60}")
    print("✓ Autonomous attack sequence complete")
    print(f"{'='*60}\n")


def interactive_mode():
    """Interactive mode for manual control"""
    oc = OpenClawAutonomous()
    
    print("\n" + "="*60)
    print("🦞 OPENCLAW AUTONOMOUS CONTROL + GROQ INTEGRATION")
    print("="*60)
    print(f"\nGroq API Key: {'✓ Configured' if oc.groq_api_key else '✗ Not set'}")
    print(f"Groq Model: {oc.groq_model}")
    print("\nCommands:")
    print("  groq <task>         - 🆓 FREE coding agent (Pi + Groq)")
    print("  groq-i              - 🆓 Interactive Groq coding session")
    print("  code <task>         - Coding agent (default: Groq)")
    print("  agent <task>        - Run autonomous agent")
    print("  lilith <prompt>     - LILITH → OpenClaw attack")
    print("  gateway start/stop  - Control gateway")
    print("  status              - Check status")
    print("  exit                - Quit")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("\033[95mopenclaw-auto>\033[0m ").strip()
            
            if not user_input:
                continue
            elif user_input.lower() == 'exit':
                oc.stop()
                break
            elif user_input.lower() == 'status':
                print(f"Gateway: {'running' if oc.check_gateway() else 'stopped'}")
                print(f"Groq: {'✓ Ready' if oc.groq_api_key else '✗ No API key'}")
                print(f"Pi: {'✓ Installed' if oc.check_pi_installed() else '✗ Not installed'}")
            elif user_input.lower() == 'gateway start':
                oc.start_gateway()
            elif user_input.lower() == 'gateway stop':
                oc.stop()
            elif user_input.lower() == 'groq-i':
                # Interactive Groq session
                oc.run_groq_coding_agent("", interactive=True)
            elif user_input.lower().startswith('groq '):
                # Groq coding task
                task = user_input[5:].strip()
                oc.run_groq_coding_agent(task, interactive=False)
            elif user_input.lower().startswith('agent '):
                task = user_input[6:].strip()
                oc.run_autonomous_agent(task)
            elif user_input.lower().startswith('code '):
                task = user_input[5:].strip()
                # Default to Groq for FREE
                oc.run_coding_agent(task, agent_type="groq")
            elif user_input.lower().startswith('lilith '):
                prompt = user_input[7:].strip()
                lilith_to_openclaw(prompt)
            else:
                # Treat as Groq coding task
                oc.run_groq_coding_agent(user_input, interactive=False)
                
        except KeyboardInterrupt:
            print("\nInterrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import traceback
    
    try:
        if len(sys.argv) > 1:
            # Command line mode
            arg1 = sys.argv[1].lower()
            
            if arg1 == 'groq' and len(sys.argv) > 2:
                # groq <task> - run Groq coding agent
                task = ' '.join(sys.argv[2:])
                oc = OpenClawAutonomous()
                oc.run_groq_coding_agent(task, interactive=False)
            elif arg1 == 'groq-i':
                # groq-i - interactive Groq session
                oc = OpenClawAutonomous()
                oc.run_groq_coding_agent("", interactive=True)
            elif arg1 == 'code' and len(sys.argv) > 2:
                # code <task> - coding agent with task
                task = ' '.join(sys.argv[2:])
                oc = OpenClawAutonomous()
                oc.run_coding_agent(task, agent_type="groq")
            elif arg1 == 'install-pi':
                # install Pi coding agent
                oc = OpenClawAutonomous()
                oc.install_pi()
            else:
                # Default: run as autonomous agent task
                task = ' '.join(sys.argv[1:])
                oc = OpenClawAutonomous()
                
                # First check if node/openclaw is set up
                print(f"\n{'='*60}")
                print(f"🦞 OPENCLAW AUTONOMOUS AGENT")
                print(f"{'='*60}")
                print(f"Task: {task}")
                print(f"{'='*60}\n")
                
                # Check prerequisites
                print("[*] Checking prerequisites...")
                
                # Check Node.js
                try:
                    node_check = subprocess.run('node --version', shell=True, capture_output=True, text=True, timeout=10)
                    if node_check.returncode != 0:
                        print("[-] ERROR: Node.js not found!")
                        print("    Install Node.js from https://nodejs.org/")
                        input("\nPress Enter to exit...")
                        sys.exit(1)
                    print(f"[+] Node.js: {node_check.stdout.strip()}")
                except Exception as e:
                    print(f"[-] Node.js check failed: {e}")
                    input("\nPress Enter to exit...")
                    sys.exit(1)
                
                # Check OpenClaw
                if not OPENCLAW_DIR.exists():
                    print(f"[-] ERROR: OpenClaw directory not found: {OPENCLAW_DIR}")
                    input("\nPress Enter to exit...")
                    sys.exit(1)
                print(f"[+] OpenClaw: {OPENCLAW_DIR}")
                
                # Check if openclaw.mjs exists
                mjs_path = OPENCLAW_DIR / 'openclaw.mjs'
                if not mjs_path.exists():
                    print(f"[-] ERROR: openclaw.mjs not found!")
                    input("\nPress Enter to exit...")
                    sys.exit(1)
                print("[+] openclaw.mjs found")
                
                # Check Groq (for fallback to coding agent)
                print(f"[+] Groq API: {'✓ Configured' if oc.groq_api_key else '✗ Not configured'}")
                print(f"[+] Pi Agent: {'✓ Installed' if oc.check_pi_installed() else '✗ Not installed'}")
                
                print("\n[*] Starting autonomous agent...")
                
                # Try OpenClaw agent first
                success = oc.run_autonomous_agent(task)
                
                if not success:
                    print("\n[!] OpenClaw agent failed. Falling back to Groq coding agent...")
                    if oc.groq_api_key:
                        oc.run_groq_coding_agent(task, interactive=False)
                    else:
                        print("[-] Groq not configured. Cannot fallback.")
                
                # Keep window open
                print("\n" + "="*60)
                input("Press Enter to close this window...")
        else:
            # Interactive mode
            interactive_mode()
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ FATAL ERROR")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}")
        input("\nPress Enter to close this window...")
