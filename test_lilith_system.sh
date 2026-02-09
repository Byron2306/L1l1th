#!/bin/bash
# LILITH System Test Suite
# Tests all components: Backend, Dashboard, OpenClaw, API Key Harvesting

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         LILITH / LuciferOS Complete System Test               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"
    
    echo -n "Testing $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        test_passed=$((test_passed + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        test_failed=$((test_failed + 1))
        return 1
    fi
}

echo "1. Backend Status Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Backend /status" "http://127.0.0.1:5000/status"
test_endpoint "OpenClaw Skills" "http://127.0.0.1:5000/openclaw/redteam-skills"
echo ""

echo "2. Dashboard Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Dashboard Home" "http://127.0.0.1:8080/"
echo ""

echo "3. AI Provider Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Chat Endpoint" "http://127.0.0.1:5000/chat" "POST" '{"message": "test"}'
echo ""

echo "4. OpenClaw Integration Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "Checking OpenClaw installation... "
if [ -d "/app/openclaw" ] && [ -f "/app/openclaw/openclaw.mjs" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    test_passed=$((test_passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    test_failed=$((test_failed + 1))
fi

echo -n "Checking OpenClaw dependencies... "
if [ -d "/app/openclaw/node_modules" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    test_passed=$((test_passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    test_failed=$((test_failed + 1))
fi
echo ""

echo "5. API Key Generator Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "Checking API Key Generator... "
if [ -f "/app/tools/api_key_generator.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    test_passed=$((test_passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    test_failed=$((test_failed + 1))
fi

echo -n "Checking API Key Harvester... "
if [ -f "/app/tools/api_key_harvester.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    test_passed=$((test_passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    test_failed=$((test_failed + 1))
fi

echo -n "Checking Self-Healing System... "
if [ -f "/app/tools/self_healing_api.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    test_passed=$((test_passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    test_failed=$((test_failed + 1))
fi
echo ""

echo "6. Configuration Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "Checking config file... "
if [ -f "/app/config/lucifera.conf" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    test_passed=$((test_passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    test_failed=$((test_failed + 1))
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed: $test_passed${NC}"
echo -e "${RED}Failed: $test_failed${NC}"
echo -e "Total:  $((test_passed + test_failed))"
echo ""

if [ $test_failed -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ SOME TESTS FAILED${NC}"
    exit 1
fi
