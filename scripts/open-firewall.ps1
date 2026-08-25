# Windows Güvenlik Duvarı 8080'i LAN'a açar. TELEFON için bir kez, YÖNETİCİ olarak çalıştırın:
#   Sağ tık → Run with PowerShell  (veya: Start-Process powershell -Verb RunAs)
# Sonra .\scripts\open-demo.ps1 açıksa telefonda: http://192.168.1.8:8080

$ErrorActionPreference = "Stop"
$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Yonetici izni gerekli. UAC penceresini onaylayin."
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

$name = "HavaDurumu nginx demo 8080"
netsh advfirewall firewall delete rule name=$name | Out-Null
netsh advfirewall firewall add rule name=$name dir=in action=allow protocol=TCP localport=8080 profile=private,public
Write-Host "Tamam. Firewall 8080 acildi."
Write-Host "Telefon (ayni Wi-Fi, mobil veri KAPALI): http://192.168.1.8:8080"
Write-Host "open-demo.ps1 penceresi acik kalsin."
pause
