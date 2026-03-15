#!/bin/sh
set -e
# healthcheck.sh

failed=0
PORT="${NGINX_PORT:-80}"
HOST="${NGINX_HOST:-127.0.0.1}"

check_http() {
    name="$1"
    host_header="$2"
    url="http://${HOST}:${PORT}/health"

    if curl -sf -o /dev/null --connect-timeout 3 -H "Host: $host_header" "$url" 2>/dev/null; then
        echo "  ✓  $name ($host_header)"
    else
        echo "  ✕  $name ($host_header)"
        failed=1
    fi
}

echo "=== Checking legal litigation APIs ==="
check_http "Cases"       "cases.halcyon-pierce.internal"
check_http "Motion filings"     "motions.halcyon-pierce.internal"
check_http "Judge rulings"     "rulings.halcyon-pierce.internal"
check_http "Case Experts"     "experts.halcyon-pierce.internal"
check_http "Evidence"    "evidence.halcyon-pierce.internal"
check_http "Case Depositions" "depositions.halcyon-pierce.internal"
check_http "Citations"   "citations.halcyon-pierce.internal"
echo "========================================"

if [ "$failed" -ne 0 ]; then
    echo "Some services are not healthy."
    exit 1
fi
echo "All services are healthy."
exit 0
