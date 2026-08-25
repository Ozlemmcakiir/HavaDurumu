# Gökyüzü'nü Minikube içinde Helm + nginx Ingress ile kurar / günceller.
# Kullanım (proje kökünden):  .\scripts\deploy.ps1
#
# Canlı site Azure'dadır. Bu script yalnızca Minikube eğitim kurulumudur.

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\bin;" + $env:Path

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Image = "havadurumu:0.1.0"
$Release = "bilgeadam"
$Chart = "charts/havadurumu"

Write-Host "==> Minikube durumu"
$minikubeOk = $false
try {
    $status = minikube status --format "{{.Host}}" 2>$null
    if ($status -eq "Running") { $minikubeOk = $true }
} catch { }

if (-not $minikubeOk) {
    Write-Host "Minikube ayakta degil, docker surucusuyle baslatiliyor..."
    minikube start --driver=docker
}

Write-Host "==> nginx Ingress addon"
minikube addons enable ingress

Write-Host "==> Ingress controller bekleniyor"
kubectl wait --namespace ingress-nginx `
    --for=condition=ready pod `
    --selector=app.kubernetes.io/component=controller `
    --timeout=180s

Write-Host "==> Imaj kumenin icine derleniyor: $Image"
minikube image build -t $Image $Root

Write-Host "==> Helm chart lint"
helm lint $Chart

Write-Host "==> Helm kurulum / guncelleme: $Release"
helm upgrade --install $Release $Chart --wait --timeout 3m

Write-Host ""
Write-Host "Kurulum:"
helm list
Write-Host ""
kubectl get pods,svc,ingress -l app=havadurumu
Write-Host ""
Write-Host "Minikube egitim kurulumu bitti. Canli site Azure:"
Write-Host "  Jenkins DEPLOY_AZURE  veya  .\scripts\deploy-azure.ps1"
Write-Host "  https://<AZURE_APP_NAME>.azurewebsites.net"
