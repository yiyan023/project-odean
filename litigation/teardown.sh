#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Legal AI Litigation Strategy Teardown ==="

# Stop and remove containers
docker compose down -v --remove-orphans

echo "=== Teardown Complete ==="
