# gokyuzu release'ini kumeden kaldirir. Imaj silinmez.
$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\bin;" + $env:Path

helm uninstall gokyuzu
Write-Host "Release kaldirildi. Tekrar kurmak icin: .\scripts\deploy.ps1"
