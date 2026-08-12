#!/bin/bash
# MDUMENI Backend — Cloudflare Workers Setup Verification Script

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  MDUMENI Backend — Cloudflare Workers Setup Verification"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is MISSING"
        return 1
    fi
}

# Track status
ERRORS=0

echo "Checking required files..."
echo ""

# Check all critical files
check_file "wrangler.toml" || ((ERRORS++))
check_file "package.json" || ((ERRORS++))
check_file "worker.js" || ((ERRORS++))
check_file "index.js" || ((ERRORS++))
check_file "api_main.py" || ((ERRORS++))

echo ""
echo "Checking configuration..."
echo ""

# Check if wrangler.toml has zone_id
if grep -q 'zone_id = ""' wrangler.toml; then
    echo -e "${YELLOW}⚠${NC} wrangler.toml: zone_id is empty (needs Cloudflare Zone ID)"
    ((ERRORS++))
else
    echo -e "${GREEN}✓${NC} wrangler.toml: zone_id appears to be configured"
fi

# Check if package.json has correct scripts
if grep -q '"dev": "wrangler dev"' package.json; then
    echo -e "${GREEN}✓${NC} package.json: dev script configured"
else
    echo -e "${YELLOW}⚠${NC} package.json: dev script missing"
fi

echo ""
echo "Quick setup commands:"
echo "─────────────────────────────────────────────────────────────────────────"
echo ""
echo "1. Install dependencies:"
echo "   ${YELLOW}npm install${NC}"
echo ""
echo "2. Update wrangler.toml with your Cloudflare Zone ID:"
echo "   Edit wrangler.toml and replace zone_id = '' with your actual ID"
echo ""
echo "3. Set environment variables:"
echo "   ${YELLOW}cp .env.example .env.local${NC}"
echo "   ${YELLOW}# Edit .env.local with your BACKEND_URL${NC}"
echo ""
echo "4. Test locally:"
echo "   ${YELLOW}npm run dev${NC}"
echo ""
echo "5. Deploy to production:"
echo "   ${YELLOW}npm run deploy${NC}"
echo ""
echo "─────────────────────────────────────────────────────────────────────────"
echo ""

# Summary
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to setup Cloudflare Workers.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Install Node.js dependencies: npm install"
    echo "2. Update wrangler.toml with your Cloudflare Zone ID"
    echo "3. Configure .env.local with your BACKEND_URL"
    echo "4. Test locally: npm run dev"
    echo "5. Deploy: npm run deploy"
else
    echo -e "${RED}✗ $ERRORS issue(s) found. Please review above.${NC}"
fi

echo ""
