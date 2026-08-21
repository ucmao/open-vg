#!/bin/bash

# ============================================================================
# Vidgen Systemd Deployment Script
# ============================================================================
# :  Systemd （Backend, Celery, Frontend, Admin）
# : sudo ./deploy.sh
# ============================================================================

set -e  #

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "Vidgen Systemd Deployment Script"
echo "============================================"
echo ""

#  root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}:  sudo ${NC}"
    exit 1
fi

# （）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${YELLOW}: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}: $BACKEND_DIR${NC}"
echo ""

if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}: : $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${RED}: : $BACKEND_DIR/venv${NC}"
    exit 1
fi

echo "1.  PID ..."
mkdir -p /var/log/celery
mkdir -p /var/run/celery
mkdir -p /var/log/vidgen
chown -R www-data:www-data /var/log/celery
chown -R www-data:www-data /var/run/celery
chown -R www-data:www-data /var/log/vidgen
echo -e "${GREEN}✓ ${NC}"
echo ""

#  service
echo "2.  Systemd ..."

# （ -> ）
declare -A services=(
    ["backend"]="vidgen-backend"
    ["web"]="vidgen-web"
    ["admin"]="vidgen-admin"
    ["celery-worker"]="celery-worker"
    ["celery-beat"]="celery-beat"
    ["flower"]="flower"
)

for source_name in "${!services[@]}"; do
    target_name="${services[$source_name]}"
    service_file="$SCRIPT_DIR/${source_name}.service"
    target_file="/etc/systemd/system/${target_name}.service"
    
    if [ -f "$service_file" ]; then
        echo "    ${source_name}.service → ${target_name}.service..."
        
        sed "s|/path/to/vidgen|$PROJECT_ROOT|g" "$service_file" > "$target_file"
        
        echo -e "   ${GREEN}✓ ${target_name}.service ${NC}"
    else
        echo -e "   ${YELLOW}⚠ ${source_name}.service ，${NC}"
    fi
done

echo ""

#  systemd
echo "3.  Systemd..."
systemctl daemon-reload
echo -e "${GREEN}✓ Systemd ${NC}"
echo ""

# Start
echo "============================================"
echo "！"
echo "============================================"
echo ""
echo "："
echo "  :"
echo "  - vidgen-backend      (FastAPI  API)"
echo "  - celery-worker       (Celery Worker )"
echo "  - vidgen-web          (Nuxt C ， 3000)"
echo "  - vidgen-admin        (Nuxt  admin， 3001)"
echo ""
echo "  :"
echo "  - celery-beat         (Celery Beat )"
echo "  - flower              (Flower )"
echo ""
echo "："
echo "  Start:  sudo systemctl start vidgen-backend celery-worker vidgen-web vidgen-admin"
echo "  Stop:  sudo systemctl stop vidgen-backend celery-worker vidgen-web vidgen-admin"
echo "  :  sudo systemctl status vidgen-backend celery-worker vidgen-web vidgen-admin"
echo "  View Logs:  sudo journalctl -u celery-worker -f"
echo "  :  sudo systemctl enable vidgen-backend celery-worker vidgen-web vidgen-admin"
echo ""
echo "Management Script："
echo "  ./manage-services.sh start"
echo "  ./manage-services.sh status"
echo ""

read -p "Start (backend, celery-worker, frontend, admin)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Start..."
    systemctl start vidgen-backend
    systemctl start celery-worker
    systemctl start vidgen-web
    systemctl start vidgen-admin
    sleep 2
    echo ""
    systemctl status vidgen-backend celery-worker vidgen-web vidgen-admin --no-pager
fi

echo ""
read -p "? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "..."
    systemctl enable vidgen-backend
    systemctl enable celery-worker
    systemctl enable vidgen-web
    systemctl enable vidgen-admin
    echo -e "${GREEN}✓ ${NC}"
fi

echo ""
echo -e "${GREEN}！${NC}"
