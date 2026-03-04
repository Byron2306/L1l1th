#!/bin/bash
#===============================================================================
# LILITH ETERNAL - Quick Setup Script
#===============================================================================
# Just run: ./setup.sh
#===============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}"
echo "============================================"
echo "      LILITH ETERNAL - Docker Setup"
echo "============================================"
echo -e "${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found! Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose not found! Please install it.${NC}"
    exit 1
fi

# Check RAM
TOTAL_RAM=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "8")
echo -e "${GREEN}Detected RAM: ${TOTAL_RAM}GB${NC}"

if [ "$TOTAL_RAM" -lt 4 ]; then
    echo -e "${YELLOW}Warning: Less than 4GB RAM. Performance may be poor.${NC}"
fi

# Start services
echo -e "${GREEN}Starting LILITH ETERNAL...${NC}"

if docker compose version &> /dev/null 2>&1; then
    docker compose up -d
else
    docker-compose up -d
fi

echo ""
echo -e "${GREEN}Waiting for model download (this takes a few minutes on first run)...${NC}"
echo "You can check progress with: docker logs -f lilith-model-loader"
echo ""

# Wait for services
sleep 10

# Check if running
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   LILITH ETERNAL is ready!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "   Access at: ${YELLOW}http://localhost:5000${NC}"
    echo ""
else
    echo -e "${YELLOW}Services starting... May take a few minutes.${NC}"
    echo "Check status with: docker-compose ps"
    echo "View logs with: docker-compose logs -f"
fi
