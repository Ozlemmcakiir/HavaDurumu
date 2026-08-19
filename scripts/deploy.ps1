# Gökyüzü'nü Minikube içinde Helm ile kurar / günceller.
# Kullanım (proje kökünden):  .\scripts\deploy.ps1

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
kubectl get pods,svc,configmap,sa -l app=havadurumu
Write-Host ""
Write-Host "Uygulamayi acmak icin:"
Write-Host "  kubectl port-forward svc/havadurumu 8080:8000"
Write-Host "  http://127.0.0.1:8080"
