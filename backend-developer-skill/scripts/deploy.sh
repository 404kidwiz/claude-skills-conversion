#!/bin/bash
# Deployment Script for Backend Applications
# Supports Docker, Kubernetes, AWS, Google Cloud

set -e

# Configuration
PROJECT_NAME="${PROJECT_NAME:-api-service}"
FRAMEWORK="${FRAMEWORK:-express}"
ENV="${ENV:-production}"
REGISTRY="${REGISTRY:-gcr.io/my-project}"
DOCKER_IMAGE="${REGISTRY}/${PROJECT_NAME}:${ENV}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: ${DOCKER_IMAGE}"

    docker build \
        --build-arg ENV=${ENV} \
        --build-arg NODE_ENV=${ENV} \
        -t ${DOCKER_IMAGE} \
        .

    log_info "Docker image built successfully"
}

# Run tests
run_tests() {
    log_info "Running tests..."

    if [ "${FRAMEWORK}" = "express" ]; then
        docker run --rm ${DOCKER_IMAGE} npm test
    elif [ "${FRAMEWORK}" = "fastapi" ]; then
        docker run --rm ${DOCKER_IMAGE} pytest -v
    fi

    log_info "Tests passed"
}

# Push to registry
push_image() {
    log_info "Pushing image to registry: ${REGISTRY}"

    docker push ${DOCKER_IMAGE}

    log_info "Image pushed successfully"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    kubectl set image deployment/${PROJECT_NAME} ${PROJECT_NAME}=${DOCKER_IMAGE} -n ${ENV}

    kubectl rollout status deployment/${PROJECT_NAME} -n ${ENV}

    log_info "Deployment successful"
}

# Deploy to AWS (ECS)
deploy_aws() {
    log_info "Deploying to AWS ECS..."

    aws ecs update-service \
        --cluster ${PROJECT_NAME}-${ENV} \
        --service ${PROJECT_NAME} \
        --force-new-deployment

    log_info "AWS deployment successful"
}

# Deploy to Google Cloud (Cloud Run)
deploy_gcp() {
    log_info "Deploying to Google Cloud Run..."

    gcloud run deploy ${PROJECT_NAME} \
        --image ${DOCKER_IMAGE} \
        --platform managed \
        --region ${REGION:-us-central1} \
        --allow-unauthenticated

    log_info "GCP deployment successful"
}

# Health check
health_check() {
    log_info "Running health check..."

    if [ "${FRAMEWORK}" = "express" ]; then
        curl -f http://localhost:8080/health || exit 1
    elif [ "${FRAMEWORK}" = "fastapi" ]; then
        curl -f http://localhost:8080/api/v1/health || exit 1
    fi

    log_info "Health check passed"
}

# Rollback deployment
rollback() {
    log_info "Rolling back deployment..."

    if command -v kubectl &> /dev/null; then
        kubectl rollout undo deployment/${PROJECT_NAME} -n ${ENV}
    fi

    log_info "Rollback completed"
}

# Main deployment flow
main() {
    local SKIP_TESTS=${SKIP_TESTS:-false}
    local PLATFORM=${PLATFORM:-kubernetes}

    check_prerequisites

    build_image

    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    fi

    push_image

    case $PLATFORM in
        kubernetes)
            deploy_kubernetes
            ;;
        aws)
            deploy_aws
            ;;
        gcp)
            deploy_gcp
            ;;
        *)
            log_error "Unsupported platform: ${PLATFORM}"
            exit 1
            ;;
    esac

    health_check
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --platform)
            PLATFORM=$2
            shift 2
            ;;
        --rollback)
            rollback
            exit 0
            ;;
        --health-check)
            health_check
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

main
