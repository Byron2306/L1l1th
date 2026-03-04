#!/bin/bash
#===============================================================================
# LILITH ETERNAL - Full Setup Script
# Includes: Ollama + Stable Diffusion + Wav2Lip
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}"
cat << 'EOF'
    ██╗     ██╗██╗     ██╗████████╗██╗  ██╗
    ██║     ██║██║     ██║╚══██╔══╝██║  ██║
    ██║     ██║██║     ██║   ██║   ███████║
    ██║     ██║██║     ██║   ██║   ██╔══██║
    ███████╗██║███████╗██║   ██║   ██║  ██║
    ╚══════╝╚═╝╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝
           E T E R N A L
EOF
echo -e "${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker not found!${NC}"
    echo "Install: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check GPU
echo -e "${CYAN}[*] Checking GPU...${NC}"
if docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi &> /dev/null; then
    echo -e "${GREEN}[✓] NVIDIA GPU detected${NC}"
    GPU_AVAILABLE=true
else
    echo -e "${YELLOW}[!] No GPU detected. Will use CPU-only mode.${NC}"
    GPU_AVAILABLE=false
fi

# Choose deployment
echo ""
if [ "$GPU_AVAILABLE" = true ]; then
    echo -e "${GREEN}GPU Available - Deploying FULL stack:${NC}"
    echo "  • Ollama (chat)"
    echo "  • Stable Diffusion (local images)"
    echo "  • Wav2Lip (lip-sync)"
    echo "  • Edge TTS (voice)"
    COMPOSE_FILE="docker-compose.full.yml"
else
    echo -e "${YELLOW}CPU Only - Deploying BASIC stack:${NC}"
    echo "  • Ollama (chat)"
    echo "  • AI Horde (external images)"
    echo "  • Edge TTS (voice)"
    COMPOSE_FILE="docker-compose.yml"
fi

echo ""
read -p "Continue? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 0
fi

# Create directories
echo -e "${CYAN}[*] Creating directories...${NC}"
mkdir -p avatars sd_config

# Start deployment
echo -e "${CYAN}[*] Starting containers...${NC}"
if docker compose version &> /dev/null 2>&1; then
    docker compose -f $COMPOSE_FILE up -d
else
    docker-compose -f $COMPOSE_FILE up -d
fi

# Wait for services
echo -e "${CYAN}[*] Waiting for services to initialize...${NC}"
echo "    This may take several minutes on first run (downloading models)..."
echo ""

# Monitor progress
sleep 10

# Check health
MAX_ATTEMPTS=60
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 5
    ((ATTEMPT++))
done
echo ""

# Final status
echo ""
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            LILITH ETERNAL is ready!                      ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║  Access at: ${YELLOW}http://localhost:5000${GREEN}                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    
    if [ "$GPU_AVAILABLE" = true ]; then
        echo ""
        echo -e "${CYAN}Additional interfaces:${NC}"
        echo "  • Stable Diffusion: http://localhost:7860"
        echo "  • Ollama API: http://localhost:11434"
    fi
else
    echo -e "${YELLOW}[!] Services still starting...${NC}"
    echo ""
    echo "Check status:"
    echo "  docker compose -f $COMPOSE_FILE ps"
    echo "  docker compose -f $COMPOSE_FILE logs -f"
fi

echo ""
echo -e "${RED}ETERNAL - UNLIMITED - UNCENSORED${NC}"
