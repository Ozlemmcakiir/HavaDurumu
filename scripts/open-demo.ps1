# nginx Ingress'i laptop'a bağlar. Deploy'dan SONRA çalıştırın; pencere açık kalsın.
# Laptop:  http://havadurumu.localtest.me:8080
# Telefon (aynı Wi-Fi): http://<bu-laptop-Wi-Fi-IP>:8080

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\bin;" + $env:Path

$DemoHost = "havadurumu.localtest.me"
$LocalPort = 8080
$LanIp = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.InterfaceAlias -eq "Wi-Fi" -and $_.PrefixOrigin -ne "WellKnown" } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $LanIp) {
    $LanIp = (Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object {
            $_.IPAddress -like "192.168.*" -and
            $_.InterfaceAlias -notlike "*vEthernet*" -and
            $_.PrefixOrigin -ne "WellKnown"
        } |
        Select-Object -First 1 -ExpandProperty IPAddress)
}

Write-Host "nginx Ingress dinleniyor (LAN acik, 0.0.0.0)"
Write-Host "  Laptop : http://${DemoHost}:${LocalPort}"
if ($LanIp) {
    Write-Host "  Telefon (ayni Wi-Fi, mobil veri KAPALI): http://${LanIp}:${LocalPort}"
}
Write-Host "Akis: tarayici -> nginx -> Service -> Flet pod"
Write-Host "Bu pencereyi kapatmayin."
Write-Host ""

kubectl port-forward --address 0.0.0.0 -n ingress-nginx svc/ingress-nginx-controller "${LocalPort}:80"
