#!/bin/bash
# Frontend Deployment Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
APP_NAME="${APP_NAME:-frontend-app}"
ENV="${ENV:-production}"
BUILD_DIR="${BUILD_DIR:-dist}"

# Logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Build application
build_app() {
    log_info "Building application..."

    npm run build

    log_info "Build complete"
}

# Run tests
run_tests() {
    log_info "Running tests..."

    npm test -- --passWithNoTests --ci

    log_info "Tests passed"
}

# Check code quality
check_quality() {
    log_info "Running linter..."

    npm run lint

    log_info "Linting passed"

    log_info "Running formatter check..."

    npm run format:check

    log_info "Formatting check passed"
}

# Deploy to Vercel
deploy_vercel() {
    log_info "Deploying to Vercel..."

    vercel --prod --token=$VERCEL_TOKEN

    log_info "Vercel deployment complete"
}

# Deploy to Netlify
deploy_netlify() {
    log_info "Deploying to Netlify..."

    netlify deploy --prod --dir=$BUILD_DIR

    log_info "Netlify deployment complete"
}

# Deploy to AWS S3
deploy_s3() {
    log_info "Deploying to AWS S3..."

    aws s3 sync $BUILD_DIR s3://$S3_BUCKET --delete

    # Invalidate CloudFront cache
    if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
    fi

    log_info "S3 deployment complete"
}

# Deploy to GitHub Pages
deploy_github_pages() {
    log_info "Deploying to GitHub Pages..."

    npm run deploy

    log_info "GitHub Pages deployment complete"
}

# Main deployment
main() {
    local SKIP_TESTS=${SKIP_TESTS:-false}
    local SKIP_QUALITY=${SKIP_QUALITY:-false}
    local PLATFORM=${PLATFORM:-vercel}

    check_quality

    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    fi

    build_app

    case $PLATFORM in
        vercel)
            deploy_vercel
            ;;
        netlify)
            deploy_netlify
            ;;
        s3)
            deploy_s3
            ;;
        github)
            deploy_github_pages
            ;;
        *)
            log_error "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-quality)
            SKIP_QUALITY=true
            shift
            ;;
        --platform)
            PLATFORM=$2
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

main
