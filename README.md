# Gökyüzü — Hava Durumu

Open-Meteo verisiyle çalışan Flet web uygulaması. Yerel kümede **Minikube + Helm** ile açılır.

```
Python kodu → Docker imajı (havadurumu:0.1.0)
            → Helm chart (havadurumu)
            → release (bilgeadam)
            → 2 pod + Service
            → tarayıcı (port-forward)
```

Chart adı tarif, release adı o tarifin bu kümedeki kurulumudur.

## Proje yapısı

```
HavaDurumu/
├── main.py                 # giriş noktası
├── weather_app.py          # arayüz
├── location_service.py     # şehir arama
├── weather_service.py      # hava durumu API
├── weather_utils.py        # ikon / tema
├── assets/                 # logo
├── Dockerfile              # imaj (port 8000)
├── charts/havadurumu/      # Helm paketi  ← asıl kurulum
│   ├── Chart.yaml
│   ├── values.yaml         # replicaCount, imaj, port
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── serviceaccount.yaml
│       └── ingress.yaml    # kapalı
├── k8s/havadurumu.yaml     # Helm öncesi düz YAML (referans)
└── scripts/deploy.ps1      # minikube image build + helm install
```

## Minikube + Helm (önerilen)

Önkoşul: Docker Desktop ayakta, `minikube` ve `helm` PATH'te (`%USERPROFILE%\bin` yeterli).

Proje kökünden:

```powershell
.\scripts\deploy.ps1
```

Script şunları yapar:

1. Minikube yoksa `minikube start --driver=docker`
2. `minikube image build -t havadurumu:0.1.0 .` — imaj kümenin Docker'ına gider (`imagePullPolicy: Never`)
3. `helm lint charts/havadurumu`
4. `helm upgrade --install bilgeadam charts/havadurumu`

Uygulamayı açmak (pencere açık kalsın):

```powershell
kubectl port-forward svc/havadurumu 8080:8000
```

Tarayıcı: [http://127.0.0.1:8080](http://127.0.0.1:8080) — varsayılan şehir Ankara.

Adım adım elle:

```powershell
minikube start --driver=docker
minikube image build -t havadurumu:0.1.0 .
helm upgrade --install bilgeadam charts/havadurumu
kubectl get pods,svc -l app=havadurumu
kubectl port-forward svc/havadurumu 8080:8000
```

### Sık komutlar

| Komut | Ne bakar? |
| --- | --- |
| `minikube status` | Küme ayakta mı? |
| `helm list -A` | Release'ler — `bilgeadam` görünmeli |
| `kubectl get pods -l app=havadurumu` | 2 pod yeşil mi? |
| `helm upgrade --install bilgeadam charts/havadurumu` | Değer değişince yeniden uygula |
| `helm uninstall bilgeadam` | Kaldır (`scripts\uninstall.ps1`) |

Ölçeklemek: `charts/havadurumu/values.yaml` içinde `replicaCount: 3` yapıp `helm upgrade --install bilgeadam charts/havadurumu`.

## Yerel Python (küme olmadan)

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 main.py
```

## Sadece Docker

```powershell
docker build -t havadurumu:0.1.0 .
docker run --rm -p 8080:8000 havadurumu:0.1.0
```

Konteyner 8000 dinler; laptop'ta 8080'e map edilir.
