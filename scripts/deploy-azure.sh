#!/bin/sh
# Linux Jenkins: ACR push + App Service.
# Kullanim: sh scripts/deploy-azure.sh <RG> <ACR> <APP>
# veya env: AZURE_RESOURCE_GROUP / AZURE_ACR_NAME / AZURE_APP_NAME
set -e

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT"

if [ -n "${1:-}" ]; then AZURE_RESOURCE_GROUP="$1"; export AZURE_RESOURCE_GROUP; fi
if [ -n "${2:-}" ]; then AZURE_ACR_NAME="$2"; export AZURE_ACR_NAME; fi
if [ -n "${3:-}" ]; then AZURE_APP_NAME="$3"; export AZURE_APP_NAME; fi

load_env_file() {
    file="$1"
    [ -f "$file" ] || return 0
    while IFS= read -r line || [ -n "$line" ]; do
        line=$(printf '%s' "$line" | tr -d '\r')
        case "$line" in
            ''|\#*) continue ;;
        esac
        key=${line%%=*}
        val=${line#*=}
        eval "cur=\${$key:-}"
        if [ -z "$cur" ]; then
            export "$key=$val"
        fi
    done < "$file"
}

load_env_file "$ROOT/scripts/azure.env"

if ! command -v az >/dev/null 2>&1; then
    echo "Azure CLI yok. Jenkins Linux agent'a azure-cli kurun."
    exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
    echo "Docker yok. Agent docker push yapabilmeli."
    exit 1
fi

missing=""
[ -z "${AZURE_RESOURCE_GROUP:-}" ] && missing="$missing AZURE_RESOURCE_GROUP"
[ -z "${AZURE_ACR_NAME:-}" ] && missing="$missing AZURE_ACR_NAME"
[ -z "${AZURE_APP_NAME:-}" ] && missing="$missing AZURE_APP_NAME"
if [ -n "$missing" ]; then
    echo "Eksik:$missing"
    echo "Jenkins Build with Parameters: AZURE_RESOURCE_GROUP, AZURE_ACR_NAME, AZURE_APP_NAME doldurun."
    echo "Canli URL azurewebsites.net — http://havadurumu.localtest.me:8080 Azure DEGILDIR."
    exit 1
fi

AZURE_ACR_NAME=$(printf '%s' "$AZURE_ACR_NAME" | tr '[:upper:]' '[:lower:]')
IMAGE_TAG=${IMAGE_TAG:-0.1.0}
IMAGE_REPO=${IMAGE_REPO:-havadurumu}
LOCAL_IMAGE="${IMAGE_REPO}:${IMAGE_TAG}"
ACR_LOGIN="${AZURE_ACR_NAME}.azurecr.io"
REMOTE_IMAGE="${ACR_LOGIN}/havadurumu:${IMAGE_TAG}"
REMOTE_LATEST="${ACR_LOGIN}/havadurumu:0.1.0"

if [ -n "${AZURE_CLIENT_ID:-}" ] && [ -n "${AZURE_CLIENT_SECRET:-}" ] && [ -n "${AZURE_TENANT_ID:-}" ]; then
    echo "==> Service principal ile az login"
    az login --service-principal \
        --username "$AZURE_CLIENT_ID" \
        --password "$AZURE_CLIENT_SECRET" \
        --tenant "$AZURE_TENANT_ID" \
        --output none
    if [ -n "${AZURE_SUBSCRIPTION_ID:-}" ]; then
        az account set --subscription "$AZURE_SUBSCRIPTION_ID" --output none
    fi
else
    if ! az account show --output none 2>/dev/null; then
        echo "Azure oturumu yok. Jenkins'e AZURE_CLIENT_ID / SECRET / TENANT_ID ekleyin."
        exit 1
    fi
fi

if ! docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then
    echo "Yerel imaj yok: $LOCAL_IMAGE"
    exit 1
fi

echo "==> ACR login $AZURE_ACR_NAME"
az acr login --name "$AZURE_ACR_NAME"

echo "==> Push $REMOTE_IMAGE"
docker tag "$LOCAL_IMAGE" "$REMOTE_IMAGE"
docker tag "$LOCAL_IMAGE" "$REMOTE_LATEST"
docker push "$REMOTE_IMAGE"
docker push "$REMOTE_LATEST"

echo "==> App Service $AZURE_APP_NAME"
az webapp config container set \
    --name "$AZURE_APP_NAME" \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --docker-custom-image-name "$REMOTE_IMAGE" \
    --output none

az webapp restart --name "$AZURE_APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --output none

echo "Azure deploy bitti."
echo "CANLI URL (bunu acin, localtest.me degil):"
echo "  https://${AZURE_APP_NAME}.azurewebsites.net"
