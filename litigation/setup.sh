#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Legal AI Litigation Strategy Setup ==="
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Error: docker is not installed"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Error: docker compose is not available"; exit 1; }

# Generate seed data if needed (writes to environment/_seed_data/)
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

echo "Building Docker images..."
docker compose build
echo "Docker images built successfully ✓"

echo "Starting containers..."
docker compose up -d
echo "Containers started successfully ✓"

# Wait for nginx (port 80); then verify each API via Host header (from host, hostnames may not resolve without /etc/hosts)
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

# Verify endpoints
echo "Verifying endpoints..."
for host in cases motions rulings experts evidence depositions citations internal; do
    if curl -sf -o /dev/null -H "Host: ${host}.halcyon-pierce.internal" "http://127.0.0.1:${NGINX_PORT}/health" 2>/dev/null; then
        echo "  ✓  ${host}.halcyon-pierce.internal"
    else
        echo "  ✕  ${host}.halcyon-pierce.internal"
    fi
done

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
echo ""
echo "From this host, either:"
echo "  1) Add to /etc/hosts:  127.0.0.1  cases.halcyon-pierce.internal motions.halcyon-pierce.internal rulings.halcyon-pierce.internal experts.halcyon-pierce.internal evidence.halcyon-pierce.internal depositions.halcyon-pierce.internal citations.halcyon-pierce.internal internal.halcyon-pierce.internal"
echo "  2) Or use:  curl -H 'Host: cases.halcyon-pierce.internal' http://127.0.0.1:80/cases"
echo "From inside the Docker network (e.g. agent sandbox), the hostnames resolve to the nginx proxy."
