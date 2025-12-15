#!/bin/bash

# Travel Agent Backend - Service Manager Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Travel Agent Service Manager${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file not found!${NC}"
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT: Please update your .env file with your API keys${NC}"
        exit 1
    fi
}

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

start_postgres_only() {
    echo -e "${GREEN}🐘 Starting PostgreSQL only...${NC}"
    check_docker
    docker-compose up -d postgres
    echo ""
    echo -e "${GREEN}✅ PostgreSQL started on localhost:5432${NC}"
    echo "   Database: travelagent_db"
    echo "   User: travelagent"
    echo "   Password: password"
}

start_all_docker() {
    echo -e "${GREEN}🚀 Starting all services with Docker...${NC}"
    check_docker
    check_env

    echo "🏗️  Building Docker images..."
    docker-compose build

    echo ""
    echo "🚢 Starting all services..."
    docker-compose up -d

    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10

    echo ""
    echo -e "${GREEN}✅ Services started!${NC}"
    show_endpoints
}

start_local() {
    echo -e "${GREEN}🏠 Starting services locally...${NC}"
    check_env

    # Check if PostgreSQL is running
    if ! docker ps | grep -q travel-agent-db; then
        echo "Starting PostgreSQL..."
        start_postgres_only
        echo ""
    fi

    # Load environment variables
    export $(grep -v '^#' .env | xargs)

    # Start services in background using screen or tmux if available
    if command -v tmux &> /dev/null; then
        echo "Starting services in tmux sessions..."
        tmux new-session -d -s travel-agent-gateway "cd api-gateway && python main.py"
        tmux new-session -d -s travel-agent-chat "cd services/chat-service && python main.py"
        tmux new-session -d -s travel-agent-flight "cd services/flight-service && python main.py"
        tmux new-session -d -s travel-agent-hotel "cd services/hotel-service && python main.py"
        tmux new-session -d -s travel-agent-weather "cd services/weather-service && python main.py"
        tmux new-session -d -s travel-agent-user "cd services/user-service && python main.py"
        echo ""
        echo -e "${GREEN}✅ Services started in tmux sessions${NC}"
        echo "   View sessions: tmux ls"
        echo "   Attach to session: tmux attach -t travel-agent-gateway"
    else
        echo -e "${YELLOW}⚠️  tmux not found. Please install tmux or start services manually:${NC}"
        echo ""
        echo "Terminal 1: cd api-gateway && python main.py"
        echo "Terminal 2: cd services/chat-service && python main.py"
        echo "Terminal 3: cd services/flight-service && python main.py"
        echo "Terminal 4: cd services/hotel-service && python main.py"
        echo "Terminal 5: cd services/weather-service && python main.py"
        echo "Terminal 6: cd services/user-service && python main.py"
    fi
}

stop_services() {
    echo -e "${YELLOW}🛑 Stopping services...${NC}"

    # Stop Docker services
    if docker ps | grep -q travel-agent; then
        docker-compose down
        echo -e "${GREEN}✅ Docker services stopped${NC}"
    fi

    # Stop tmux sessions if they exist
    if command -v tmux &> /dev/null; then
        tmux kill-session -t travel-agent-gateway 2>/dev/null || true
        tmux kill-session -t travel-agent-chat 2>/dev/null || true
        tmux kill-session -t travel-agent-flight 2>/dev/null || true
        tmux kill-session -t travel-agent-hotel 2>/dev/null || true
        tmux kill-session -t travel-agent-weather 2>/dev/null || true
        tmux kill-session -t travel-agent-user 2>/dev/null || true
        echo -e "${GREEN}✅ Tmux sessions stopped${NC}"
    fi
}

show_logs() {
    echo -e "${BLUE}📊 Showing Docker logs (Ctrl+C to exit)...${NC}"
    docker-compose logs -f
}

show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo ""
    docker-compose ps
}

show_endpoints() {
    echo ""
    echo -e "${BLUE}📚 API Documentation:${NC}"
    echo "   - API Gateway: http://localhost:8000/docs"
    echo "   - Chat Service: http://localhost:8001/docs"
    echo "   - Flight Service: http://localhost:8002/docs"
    echo "   - Hotel Service: http://localhost:8003/docs"
    echo "   - Weather Service: http://localhost:8004/docs"
    echo "   - User Service: http://localhost:8005/docs"
    echo ""
}

show_menu() {
    print_header
    echo "Select an option:"
    echo ""
    echo "  1) Start PostgreSQL only (for local development)"
    echo "  2) Start all services with Docker"
    echo "  3) Start services locally (requires tmux)"
    echo "  4) Stop all services"
    echo "  5) View Docker logs"
    echo "  6) Show service status"
    echo "  7) Show API endpoints"
    echo "  0) Exit"
    echo ""
    read -p "Enter your choice [0-7]: " choice

    case $choice in
        1) start_postgres_only ;;
        2) start_all_docker ;;
        3) start_local ;;
        4) stop_services ;;
        5) show_logs ;;
        6) show_status ;;
        7) show_endpoints ;;
        0) echo "Goodbye! 👋"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
}

# Main script
if [ $# -eq 0 ]; then
    # No arguments, show interactive menu
    show_menu
else
    # Handle command line arguments
    case $1 in
        postgres|db) start_postgres_only ;;
        all|docker) start_all_docker ;;
        local|dev) start_local ;;
        stop|down) stop_services ;;
        logs) show_logs ;;
        status|ps) show_status ;;
        endpoints|docs) show_endpoints ;;
        *)
            echo "Usage: $0 [postgres|all|local|stop|logs|status|endpoints]"
            echo ""
            echo "Commands:"
            echo "  postgres  - Start PostgreSQL only"
            echo "  all       - Start all services with Docker"
            echo "  local     - Start services locally"
            echo "  stop      - Stop all services"
            echo "  logs      - View Docker logs"
            echo "  status    - Show service status"
            echo "  endpoints - Show API endpoints"
            echo ""
            echo "Run without arguments for interactive menu"
            ;;
    esac
fi
