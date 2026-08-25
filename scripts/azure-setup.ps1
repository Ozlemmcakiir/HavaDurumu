# Azure kaynaklarini BIR KEZ olusturur. Jenkins test/lint/docker/minikube stage'lerine dokunmaz.
#
# Onkosul: Azure hesabi + az CLI
#   winget install Microsoft.AzureCLI
#   az login
#
# Kullanim (proje kokunden):
#   .\scripts\azure-setup.ps1
#
# Cikti: scripts/azure.env  + Jenkins'e yapistirilacak service principal
# Canli URL: https://<AZURE_APP_NAME>.azurewebsites.net
# Not: Linux container icin App Service Free (F1) yetmez; plan B1 (ucretli).

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\bin;" + $env:Path

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Assert-Az {
    $az = Get-Command az -ErrorAction SilentlyContinue
    if (-not $az) {
        Write-Host "Azure CLI yok. Kur:"
        Write-Host "  winget install Microsoft.AzureCLI"
        Write-Host "Sonra yeni PowerShell: az login"
        exit 1
    }
}

function Get-AzAccountJson {
    $raw = az account show --output json 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
    return $raw | ConvertFrom-Json
}

function Import-DotEnv([string]$Path) {
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#") -or $line -notmatch "=") { return }
        $k, $v = $line.Split("=", 2)
        if (-not [Environment]::GetEnvironmentVariable($k)) {
            Set-Item -Path "Env:$k" -Value $v
        }
    }
}

Assert-Az
$acct = Get-AzAccountJson
if (-not $acct) {
    Write-Host "==> az login (tarayici acilacak)"
    az login --output none
    $acct = Get-AzAccountJson
}
if (-not $acct) {
    Write-Host "Azure oturumu yok. az login ile giris yapin."
    exit 1
}

Write-Host "Abonelik: $($acct.name)  ($($acct.id))"

Import-DotEnv (Join-Path $PSScriptRoot "azure.env")

$Location = if ($env:AZURE_LOCATION) { $env:AZURE_LOCATION } else { "westeurope" }
$Rg       = if ($env:AZURE_RESOURCE_GROUP) { $env:AZURE_RESOURCE_GROUP } else { "havadurumu-rg" }
$Plan     = if ($env:AZURE_APP_PLAN) { $env:AZURE_APP_PLAN } else { "havadurumu-plan" }
$suffix   = Get-Random -Minimum 1000 -Maximum 9999
$AcrName  = if ($env:AZURE_ACR_NAME) { $env:AZURE_ACR_NAME } else { "gokyuzuacr$suffix" }
$AppName  = if ($env:AZURE_APP_NAME) { $env:AZURE_APP_NAME } else { "gokyuzu-havadurumu-$suffix" }
$AcrName  = $AcrName.ToLower() -replace "[^a-z0-9]", ""

Write-Host "==> Resource group $Rg ($Location)"
az group create --name $Rg --location $Location --output none

Write-Host "==> Container Registry $AcrName (Basic)"
az acr create --name $AcrName --resource-group $Rg --sku Basic --admin-enabled true --output none
if ($LASTEXITCODE -ne 0) {
    Write-Host "ACR olusturma atlandi, mevcut registry deneniyor: $AcrName"
    az acr show --name $AcrName --resource-group $Rg --output none
    if ($LASTEXITCODE -ne 0) { throw "ACR $AcrName yok ve olusturulamadi." }
}

Write-Host "==> App Service plan $Plan (B1 Linux — container icin F1 yetmez)"
az appservice plan create --name $Plan --resource-group $Rg --is-linux --sku B1 --output none

$AcrLogin = "$AcrName.azurecr.io"
$imagePlaceholder = "${AcrLogin}/havadurumu:0.1.0"

Write-Host "==> Web App $AppName"
az webapp create `
    --name $AppName `
    --resource-group $Rg `
    --plan $Plan `
    --deployment-container-image-name $imagePlaceholder `
    --output none

$acrUser = az acr credential show --name $AcrName --query username --output tsv
$acrPass = az acr credential show --name $AcrName --query "passwords[0].value" --output tsv

Write-Host "==> Container ayarlari (port 8000, websocket, ACR pull)"
az webapp config appsettings set --name $AppName --resource-group $Rg --output none --settings `
    WEBSITES_PORT=8000 `
    FLET_FORCE_WEB_SERVER=true `
    FLET_SERVER_IP=0.0.0.0 `
    FLET_SERVER_PORT=8000 `
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=false `
    DOCKER_REGISTRY_SERVER_URL="https://$AcrLogin" `
    DOCKER_REGISTRY_SERVER_USERNAME="$acrUser" `
    DOCKER_REGISTRY_SERVER_PASSWORD="$acrPass"

az webapp config set --name $AppName --resource-group $Rg --web-sockets-enabled true --always-on true --output none

$envFile = Join-Path $PSScriptRoot "azure.env"
@"
AZURE_RESOURCE_GROUP=$Rg
AZURE_LOCATION=$Location
AZURE_ACR_NAME=$AcrName
AZURE_APP_NAME=$AppName
AZURE_APP_PLAN=$Plan
AZURE_SUBSCRIPTION_ID=$($acct.id)
"@ | Set-Content -Path $envFile -Encoding utf8

Write-Host "==> Jenkins service principal (RG Contributor)"
$spName = "havadurumu-jenkins"
$scope = "/subscriptions/$($acct.id)/resourceGroups/$Rg"
$spRaw = az ad sp create-for-rbac --name $spName --role Contributor --scopes $scope --output json 2>$null
if ($LASTEXITCODE -ne 0 -or -not $spRaw) {
    Write-Host "SP olusturulamadi (izin veya ad cakismasi). Jenkins icin el ile:"
    Write-Host "  az ad sp create-for-rbac --name $spName --role Contributor --scopes $scope"
    $sp = $null
} else {
    $sp = $spRaw | ConvertFrom-Json
}

$site = "https://$AppName.azurewebsites.net"
Write-Host ""
Write-Host "Azure altyapi hazir. Imaj henuz yok — Jenkins DEPLOY_AZURE veya .\scripts\deploy-azure.ps1"
Write-Host "Site (ilk deploy sonrasi): $site"
Write-Host "Isimler yazildi: scripts\azure.env"
Write-Host ""
if ($sp) {
    Write-Host "Jenkins job > Configure > Environment / Credentials:"
    Write-Host "  AZURE_CLIENT_ID=$($sp.appId)"
    Write-Host "  AZURE_CLIENT_SECRET=$($sp.password)"
    Write-Host "  AZURE_TENANT_ID=$($sp.tenant)"
    Write-Host "  AZURE_SUBSCRIPTION_ID=$($acct.id)"
    Write-Host "  AZURE_RESOURCE_GROUP=$Rg"
    Write-Host "  AZURE_ACR_NAME=$AcrName"
    Write-Host "  AZURE_APP_NAME=$AppName"
    Write-Host "Secret'i bir yere kaydedin; Azure bir daha gostermez."
}
Write-Host ""
Write-Host "Sonraki adim: docker build sonrasi .\scripts\deploy-azure.ps1"
Write-Host "veya Jenkins Build with Parameters -> DEPLOY_AZURE"
