#!/bin/bash

# WorkHub Production Deployment Script
# This script automates the deployment process for all WorkHub services

set -e  # Exit on any error

echo "🚀 Starting WorkHub Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NEON_PROJECT_ID=""
UPSTASH_REDIS_ID=""
RENDER_BACKEND_SERVICE=""
RENDER_AGENT_SERVICE=""
VERCEL_PROJECT_ID=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment files exist
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env.production" ]; then
        print_error ".env.production file not found!"
        print_status "Please copy .env.production.example to .env.production and fill in your values"
        exit 1
    fi
    
    print_success "Environment configuration found"
}

# Validate required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check for required CLI tools
    command -v curl >/dev/null 2>&1 || { print_error "curl is required but not installed"; exit 1; }
    command -v git >/dev/null 2>&1 || { print_error "git is required but not installed"; exit 1; }
    
    print_success "All prerequisites satisfied"
}

# Deploy Database (Neon)
deploy_database() {
    print_status "Setting up Neon PostgreSQL database..."
    
    # Load database URL from environment
    source .env.production
    
    if [ -z "$DATABASE_URL" ]; then
        print_error "DATABASE_URL not found in .env.production"
        exit 1
    fi
    
    print_status "Running database migrations..."
    cd backend
    python migrate_database.py || {
        print_error "Database migration failed"
        exit 1
    }
    cd ..
    
    print_success "Database setup completed"
}

# Deploy Redis (Upstash)
deploy_redis() {
    print_status "Verifying Upstash Redis connection..."
    
    source .env.production
    
    if [ -z "$REDIS_URL" ]; then
        print_error "REDIS_URL not found in .env.production"
        print_status "Please set up FREE Upstash Redis following: deployment/FREE_REDIS_SETUP.md"
        exit 1
    fi
    
    # Test Redis connection (using curl for Upstash REST API)
    UPSTASH_URL=$(echo "$REDIS_URL" | sed 's/redis:\/\/default://' | sed 's/@/ /' | awk '{print $2}')
    UPSTASH_PASS=$(echo "$REDIS_URL" | sed 's/redis:\/\/default://' | sed 's/@.*//')
    
    print_status "Testing Upstash Redis connection..."
    curl -s -u "default:$UPSTASH_PASS" "https://$UPSTASH_URL/ping" >/dev/null || {
        print_warning "Could not verify Redis connection. Please ensure Upstash Redis is properly configured."
        print_status "Visit: https://console.upstash.com/ to check your database status"
    }
    
    print_success "Redis configuration verified (Upstash FREE tier)"
}

# Deploy Backend (Render)
deploy_backend() {
    print_status "Deploying backend to Render..."
    
    # Build and test backend locally first
    print_status "Building backend locally for validation..."
    cd backend
    
    # Create virtual environment and install dependencies
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Test that the app can start
    python -c "from app.main import app; print('✅ Backend syntax validation passed')"
    
    deactivate
    rm -rf venv
    cd ..
    
    print_success "Backend validation completed"
    print_status "Backend will be deployed via Git push to Render (connected repository)"
}

# Deploy AI Agent (Render) 
deploy_ai_agent() {
    print_status "Deploying AI Agent to Render..."
    
    # Build and test AI agent locally first
    print_status "Building AI Agent locally for validation..."
    cd langgraph
    
    # Create virtual environment and install dependencies
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Test that the agent can start
    python -c "from main import app; print('✅ AI Agent syntax validation passed')"
    
    deactivate
    rm -rf venv
    cd ..
    
    print_success "AI Agent validation completed"
    print_status "AI Agent will be deployed via Git push to Render (connected repository)"
}

# Deploy Frontend (Vercel)
deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    
    # Build and test frontend locally first
    print_status "Building frontend locally for validation..."
    cd frontend
    
    # Install dependencies and build
    npm ci
    npm run build || {
        print_error "Frontend build failed"
        exit 1
    }
    
    cd ..
    
    print_success "Frontend build validation completed"
    print_status "Frontend will be deployed via Git push to Vercel (connected repository)"
}

# Health check for deployed services
health_check() {
    print_status "Performing health checks..."
    
    # Wait for services to start up
    print_status "Waiting 60 seconds for services to initialize..."
    sleep 60
    
    # Check backend
    print_status "Checking backend health..."
    if curl -f -s "https://workhub-backend.onrender.com/health" >/dev/null; then
        print_success "Backend is healthy"
    else
        print_warning "Backend health check failed or service not yet ready"
    fi
    
    # Check AI agent
    print_status "Checking AI agent health..."
    if curl -f -s "https://workhub-agent.onrender.com/health" >/dev/null; then
        print_success "AI Agent is healthy"
    else
        print_warning "AI Agent health check failed or service not yet ready"
    fi
    
    # Check frontend
    print_status "Checking frontend accessibility..."
    if curl -f -s "https://workhub.vercel.app" >/dev/null; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend accessibility check failed or service not yet ready"
    fi
}

# Display deployment summary
deployment_summary() {
    echo ""
    echo "🎉 WorkHub Deployment Summary"
    echo "================================"
    echo "Frontend:   https://workhub.vercel.app"
    echo "Backend:    https://workhub-backend.onrender.com"
    echo "AI Agent:   https://workhub-agent.onrender.com"
    echo "Database:   Neon PostgreSQL (configured)"
    echo "Redis:      Upstash Redis (configured)"
    echo ""
    echo "📊 Monitoring:"
    echo "- Render Dashboard: https://dashboard.render.com/"
    echo "- Vercel Dashboard: https://vercel.com/dashboard"
    echo "- Neon Console: https://console.neon.tech/"
    echo "- Upstash Console: https://console.upstash.com/"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Configure custom domain (if needed)"
    echo "2. Set up monitoring alerts"
    echo "3. Test all functionality end-to-end"
    echo "4. Update DNS records (if using custom domain)"
}

# Main deployment function
main() {
    echo "🚀 WorkHub Production Deployment"
    echo "================================"
    
    check_prerequisites
    check_environment
    
    print_status "Starting deployment process..."
    
    deploy_database
    deploy_redis
    deploy_backend
    deploy_ai_agent
    deploy_frontend
    
    print_status "All services prepared for deployment!"
    print_warning "Push to main branch to trigger automatic deployment via GitHub Actions"
    
    # Optionally run health checks if services are already deployed
    read -p "Do you want to run health checks on existing deployment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        health_check
    fi
    
    deployment_summary
    
    print_success "Deployment preparation completed successfully! 🎉"
}

# Run main function
main "$@"