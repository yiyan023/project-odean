#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
COMPOSE_FILE="docker-compose.yml"

echo "=== Legal AI Litigation Strategy Setup ==="
echo ""

# 1. Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not found"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

# 2. Generate seed data if needed 
if [ ! -f environment/_seed_data/cases.csv ]; then
    echo "Preparing seed data..."
    if [ -f generate_data.py ]; then
        python3 generate_data.py
    fi
    if [ ! -f environment/_seed_data/cases.csv ]; then
        echo "ERROR: environment/_seed_data/ not populated. Run: python3 generate_data.py"
        exit 1
    fi
fi

# 3. Build Docker images
echo "Building Docker images..."
docker compose -f "$COMPOSE_FILE" build --quiet
echo "Docker images built successfully ✓"

# 4. Start containers
echo "Starting containers..."
docker compose -f "$COMPOSE_FILE" up -d
echo "Containers started successfully ✓"

# 5. Wait for services to become ready
echo "Waiting for services..."
NGINX_PORT=80
for i in $(seq 1 90); do
    if curl -sf --connect-timeout 2 "http://127.0.0.1:${NGINX_PORT}/health" -H "Host: cases.halcyon-pierce.internal" >/dev/null 2>&1; then
        echo "  ✓ nginx and backend services are ready"
        break
    fi
    if [ "$i" -eq 90 ]; then
        echo "ERROR: Services did not become ready within 90 seconds"
        exit 1
    fi
    sleep 1
done

# 6. Verify endpoints
echo "Verifying endpoints..."
verify_failed=0
for host in cases motions rulings experts evidence depositions citations; do
    if curl -sf -o /dev/null -H "Host: ${host}.halcyon-pierce.internal" "http://127.0.0.1:${NGINX_PORT}/health" 2>/dev/null; then
        echo "  ✓  ${host}.halcyon-pierce.internal"
    else
        echo "  ✕  ${host}.halcyon-pierce.internal"
        verify_failed=1
    fi
done

if [ "$verify_failed" -ne 0 ]; then
    echo ""
    echo "ERROR: One or more endpoints did not respond. Setup failed."
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "APIs are available by hostname (port 80) with the following base URLs:"
echo "  Cases:      http://cases.halcyon-pierce.internal"
echo "  Motions:    http://motions.halcyon-pierce.internal"
echo "  Rulings:    http://rulings.halcyon-pierce.internal"
echo "  Experts:    http://experts.halcyon-pierce.internal"
echo "  Evidence:   http://evidence.halcyon-pierce.internal"
echo "  Depositions: http://depositions.halcyon-pierce.internal"
echo "  Citations:  http://citations.halcyon-pierce.internal"
exit 0
