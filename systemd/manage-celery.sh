#!/bin/bash

# ============================================================================
# Celery Management Script
# ============================================================================
# :  Celery
# : sudo ./manage-celery.sh {start|stop|restart|status|logs}
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICES=("celery-worker" "celery-beat" "flower")

show_help() {
    echo "Celery Management Script"
    echo ""
    echo ": sudo $0 {command} [service]"
    echo ""
    echo ":"
    echo "  start       Start"
    echo "  stop        Stop"
    echo "  restart     Restart"
    echo "  status      "
    echo "  logs        View Logs ()"
    echo "  enable      "
    echo "  disable     "
    echo ""
    echo " (，):"
    echo "  worker       celery-worker"
    echo "  beat         celery-beat"
    echo "  flower       flower"
    echo ""
    echo ":"
    echo "  sudo $0 start              # Start"
    echo "  sudo $0 restart worker     # Restart worker"
    echo "  sudo $0 logs worker        #  worker "
    echo "  sudo $0 status             # Service Status"
}

#  root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}:  sudo ${NC}"
        exit 1
    fi
}

get_services() {
    local target=$1
    case "$target" in
        worker)
            echo "celery-worker"
            ;;
        beat)
            echo "celery-beat"
            ;;
        flower)
            echo "flower"
            ;;
        ""|all)
            echo "${SERVICES[@]}"
            ;;
        *)
            echo -e "${RED}:  '$target'${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Start
cmd_start() {
    local services=$(get_services "$1")
    echo -e "${BLUE}Start...${NC}"
    for service in $services; do
        echo "  Start $service..."
        systemctl start "$service"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ $service Start${NC}"
        else
            echo -e "  ${RED}✗ $service Start${NC}"
        fi
    done
}

# Stop
cmd_stop() {
    local services=$(get_services "$1")
    echo -e "${BLUE}Stop...${NC}"
    for service in $services; do
        echo "  Stop $service..."
        systemctl stop "$service"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ $service Stop${NC}"
        else
            echo -e "  ${RED}✗ $service Stop${NC}"
        fi
    done
}

# Restart
cmd_restart() {
    local services=$(get_services "$1")
    echo -e "${BLUE}Restart...${NC}"
    for service in $services; do
        echo "  Restart $service..."
        systemctl restart "$service"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ $service Restart${NC}"
        else
            echo -e "  ${RED}✗ $service Restart${NC}"
        fi
    done
}

cmd_status() {
    local services=$(get_services "$1")
    echo -e "${BLUE}Service Status:${NC}"
    echo ""
    for service in $services; do
        systemctl status "$service" --no-pager
        echo ""
    done
}

# View Logs
cmd_logs() {
    local service_name=$1
    if [ -z "$service_name" ]; then
        service_name="worker"
    fi
    
    local full_service=$(get_services "$service_name" | head -n 1)
    
    echo -e "${BLUE} $full_service  ( Ctrl+C )...${NC}"
    echo ""
    journalctl -u "$full_service" -f
}

cmd_enable() {
    local services=$(get_services "$1")
    echo -e "${BLUE}...${NC}"
    for service in $services; do
        echo "   $service..."
        systemctl enable "$service"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ $service ${NC}"
        else
            echo -e "  ${RED}✗ $service ${NC}"
        fi
    done
}

cmd_disable() {
    local services=$(get_services "$1")
    echo -e "${BLUE}...${NC}"
    for service in $services; do
        echo "   $service..."
        systemctl disable "$service"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ $service ${NC}"
        else
            echo -e "  ${RED}✗ $service ${NC}"
        fi
    done
}

main() {
    local command=$1
    local target=$2
    
    case "$command" in
        start)
            check_root
            cmd_start "$target"
            ;;
        stop)
            check_root
            cmd_stop "$target"
            ;;
        restart)
            check_root
            cmd_restart "$target"
            ;;
        status)
            cmd_status "$target"
            ;;
        logs)
            cmd_logs "$target"
            ;;
        enable)
            check_root
            cmd_enable "$target"
            ;;
        disable)
            check_root
            cmd_disable "$target"
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo -e "${RED}:  '$command'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
