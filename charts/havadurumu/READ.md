# havadurumu Helm chart

Chart adı **havadurumu**, release adı **gokyuzu**.

```
chart  = tarif   (havadurumu)
release = kurulum (gokyuzu)
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
| `templates/ingress.yaml` | Kapalı; gerçek yayın için |
| `templates/_helpers.tpl` | Ortak isim ve etiketler |

## Kurulum

Proje kökünden:

```powershell
minikube image build -t havadurumu:0.1.0 .
helm upgrade --install gokyuzu charts/havadurumu
kubectl port-forward svc/havadurumu 8080:8000
```

Veya `scripts\deploy.ps1`.
 