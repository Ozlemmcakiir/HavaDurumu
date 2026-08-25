# havadurumu Helm chart

Chart adı **havadurumu**, release adı **bilgeadam**.

```
chart   = tarif    (havadurumu)
release = kurulum  (bilgeadam)
```

## Dosyalar

| Dosya | Görevi |
| --- | --- |
| `Chart.yaml` | Paket kimliği |
| `values.yaml` | replicaCount, imaj, port — burası değiştirilir |
| `templates/deployment.yaml` | Pod sayısını ve imajı uygular |
| `templates/service.yaml` | Pod'lara sabit kapı |
| `templates/configmap.yaml` | Flet ortam değişkenleri |
| `templates/serviceaccount.yaml` | Pod kimliği |
| `templates/ingress.yaml` | nginx Ingress — demo host `havadurumu.localtest.me` |
| `templates/NOTES.txt` | `helm install` sonrası komutlar |
| `templates/_helpers.tpl` | Ortak isim ve etiketler |

## Kurulum

Proje kökünden:

```powershell
minikube addons enable ingress
minikube image build -t havadurumu:0.1.0 .
helm upgrade --install bilgeadam charts/havadurumu
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
```

Tarayıcı: http://havadurumu.localtest.me:8080

Veya `scripts\deploy.ps1` ardından `scripts\open-demo.ps1`.
