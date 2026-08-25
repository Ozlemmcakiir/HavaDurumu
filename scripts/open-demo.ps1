# nginx Ingress'i laptop'a bağlar. Deploy'dan SONRA çalıştırın; pencere açık kalsın.
# Domain / A kaydı yok: havadurumu.localtest.me ücretsizdir ve 127.0.0.1'e gider.

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\bin;" + $env:Path

$DemoHost = "havadurumu.localtest.me"
$LocalPort = 8080

Write-Host "nginx Ingress dinleniyor -> http://${DemoHost}:${LocalPort}"
Write-Host "Akis: tarayici -> nginx -> Service -> Flet pod"
Write-Host "Bu pencereyi kapatmayin."
Write-Host ""

kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller "${LocalPort}:80"
