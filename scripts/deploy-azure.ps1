# Jenkins'in urettigi havadurumu imajini ACR'ye push eder, App Service'i gunceller.
# Jenkins: powershell ... deploy-azure.ps1 -ResourceGroup X -AcrName Y -AppName Z
#
# Canli URL: https://<AZURE_APP_NAME>.azurewebsites.net

param(
    [string]$ResourceGroup = "",
    [string]$AcrName = "",
    [string]$AppName = ""
)

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\bin;" + $env:Path

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if ($ResourceGroup) { $env:AZURE_RESOURCE_GROUP = $ResourceGroup }
if ($AcrName) { $env:AZURE_ACR_NAME = $AcrName }
if ($AppName) { $env:AZURE_APP_NAME = $AppName }

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

Import-DotEnv (Join-Path $PSScriptRoot "azure.env")

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Azure CLI yok. Agent'a kurun: winget install Microsoft.AzureCLI"
    exit 1
}

$need = @("AZURE_RESOURCE_GROUP", "AZURE_ACR_NAME", "AZURE_APP_NAME")
foreach ($k in $need) {
    $v = ([Environment]::GetEnvironmentVariable($k) + "").Trim()
    if (-not $v) {
        Write-Host "Eksik $k. Jenkins Build with Parameters icine azure-setup ciktisini yazin."
        Write-Host "Canli site: https://<AZURE_APP_NAME>.azurewebsites.net"
        exit 1
    }
    Set-Item -Path "Env:$k" -Value $v
}

$Rg      = $env:AZURE_RESOURCE_GROUP
$AcrName = $env:AZURE_ACR_NAME.ToLower()
$AppName = $env:AZURE_APP_NAME
$LocalTag = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "0.1.0" }
$LocalRepo = if ($env:IMAGE_REPO) { $env:IMAGE_REPO } else { "havadurumu" }
$LocalImage = "${LocalRepo}:${LocalTag}"
$AcrLogin = "$AcrName.azurecr.io"
$RemoteImage = "${AcrLogin}/havadurumu:${LocalTag}"
$RemoteLatest = "${AcrLogin}/havadurumu:0.1.0"

if ($env:AZURE_CLIENT_ID -and $env:AZURE_CLIENT_SECRET -and $env:AZURE_TENANT_ID) {
    Write-Host "==> Service principal ile az login"
    az login --service-principal `
        --username $env:AZURE_CLIENT_ID `
        --password $env:AZURE_CLIENT_SECRET `
        --tenant $env:AZURE_TENANT_ID `
        --output none
    if ($env:AZURE_SUBSCRIPTION_ID) {
        az account set --subscription $env:AZURE_SUBSCRIPTION_ID --output none
    }
} else {
    $acct = az account show --output json 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $acct) {
        Write-Host "Azure oturumu yok. az login veya Jenkins AZURE_CLIENT_* env."
        exit 1
    }
}

docker image inspect $LocalImage 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Yerel imaj yok: $LocalImage"
    Write-Host "Once Jenkins Docker Build veya: docker build -t ${LocalRepo}:0.1.0 -t $LocalImage ."
    exit 1
}

Write-Host "==> ACR login $AcrName"
az acr login --name $AcrName

Write-Host "==> Push $RemoteImage"
docker tag $LocalImage $RemoteImage
docker tag $LocalImage $RemoteLatest
docker push $RemoteImage
docker push $RemoteLatest

Write-Host "==> App Service imaji $AppName"
az webapp config container set `
    --name $AppName `
    --resource-group $Rg `
    --docker-custom-image-name $RemoteImage `
    --output none

az webapp restart --name $AppName --resource-group $Rg --output none

$site = "https://$AppName.azurewebsites.net"
Write-Host ""
Write-Host "Azure deploy bitti."
Write-Host "  $site"
Write-Host "Ilk acilis 1-2 dk surebilir. Laptop acik olmak zorunda degil."
Write-Host "Log: az webapp log tail --name $AppName --resource-group $Rg"
