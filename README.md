# Gökyüzü — Hava Durumu

Open-Meteo verisiyle çalışan Flet web uygulaması. Canlı adres **yalnızca Azure**:

`https://<AZURE_APP_NAME>.azurewebsites.net`

```
Python kodu → Jenkins (test, helm lint, docker build)
            → DEPLOY_AZURE → ACR + App Service
            → https://<app>.azurewebsites.net
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
├── Dockerfile              # imaj (port 8080, Azure)
├── Jenkinsfile             # test → helm lint → docker → DEPLOY_AZURE
├── tests/                  # pytest (API mock'lu, ağ gerekmez)
├── requirements-dev.txt    # pytest + requests (CI)
├── charts/havadurumu/      # Helm paketi  ← asıl kurulum
│   ├── Chart.yaml
│   ├── values.yaml         # replicaCount, imaj, port
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── serviceaccount.yaml
│       └── ingress.yaml    # eğitim; canlı yayın Azure
├── k8s/havadurumu.yaml     # Helm öncesi düz YAML (referans)
└── scripts/
    ├── deploy.ps1          # minikube + nginx ingress + helm install
    ├── open-demo.ps1       # nginx'i :8080'e bağlar (laptop + aynı Wi-Fi)
    ├── open-firewall.ps1   # telefon LAN için Windows 8080 (yönetici)
    ├── azure-setup.ps1     # bir kez: RG, ACR, App Service (B1)
    ├── deploy-azure.ps1    # Windows: ACR push + App Service
    ├── deploy-azure.sh     # Linux Jenkins: aynı iş
    ├── azure.env.example   # Azure isim şablonu (asıl azure.env git'te yok)
    ├── uninstall.ps1
    └── ci-test.sh          # Jenkins Test stage (python:3.14.7-slim içinde)
```

## Canlı yayın: Azure App Service

Tarayıcıda açılacak adres budur. Laptop / Minikube adresi kullanılmaz.

Linux container **Free F1'de çalışmaz**; setup **B1** plan açar. Domain gerekmez.

### Adım 1 — Azure CLI ve giriş

```powershell
winget install Microsoft.AzureCLI
az login
```

### Adım 2 — Altyapı (bir kez)

```powershell
cd C:\Users\merve.arslan\IdeaProjects\HavaDurumu
.\scripts\azure-setup.ps1
```

Resource group, ACR, B1 plan, Web App, websocket (Flet), `scripts\azure.env` ve Jenkins service principal üretir.

### Adım 3 — Jenkins ortam değişkenleri

Job **Configure** → Environment / Credentials. Setup'ın yazdırdığı değerler:

- `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` / `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP` / `AZURE_ACR_NAME` / `AZURE_APP_NAME`

Agent'ta **Azure CLI** ve **Docker** olmalı (push için).

### Adım 4 — Deploy

Jenkins: **Build with Parameters** → **DEPLOY_AZURE** işaretle → Build.

Veya yerelde (önce `docker build -t havadurumu:0.1.0 .`):

```powershell
.\scripts\deploy-azure.ps1
```

### Adım 5 — Site

`https://<AZURE_APP_NAME>.azurewebsites.net` — ilk açılış 1–2 dk. Laptop açık olmak zorunda değil.

Log:

```powershell
az webapp log tail --name <AZURE_APP_NAME> --resource-group havadurumu-rg
```

### Sık komutlar (eğitim kümesi, canlı site değil)

| Komut | Ne bakar? |
| --- | --- |
| `minikube status` | Küme ayakta mı? |
| `helm list -A` | Release'ler — `bilgeadam` görünmeli |
| `kubectl get pods,ingress -l app=havadurumu` | 2 pod yeşil mi, Ingress host doğru mu? |
| `helm upgrade --install bilgeadam charts/havadurumu` | Değer değişince yeniden uygula |
| `helm uninstall bilgeadam` | Kaldır (`scripts\uninstall.ps1`) |

Ölçeklemek: `charts/havadurumu/values.yaml` içinde `replicaCount: 3` yapıp `helm upgrade --install bilgeadam charts/havadurumu`.

## Yerel Python (küme olmadan)

```powershell
py -3.14 -m pip install -r requirements.txt
py -3.14 main.py
```

## Sadece Docker

```powershell
docker build -t havadurumu:0.1.0 .
docker run --rm -p 8080:8080 havadurumu:0.1.0
```

Konteyner 8080 dinler (Azure `WEBSITES_PORT` ile aynı).

## Jenkins CI

Kod Git'e düşünce (veya Jenkins'te **Build Now**) sırayla:

1. **Test** — `python:3.14.7-slim` içinde `py_compile` + pytest (Open-Meteo çağrıları mock'lanır, internet gerekmez)
2. **Helm Lint** — `alpine/helm` ile `helm lint` + `helm template`
3. **Docker Build** — `havadurumu:0.1.<BUILD_NUMBER>` ve `havadurumu:0.1.0`
4. **Deploy Azure** — `DEPLOY_AZURE` işaretliyse ACR push + App Service. Site: `https://<AZURE_APP_NAME>.azurewebsites.net`

Agent'ta Python veya Helm kurulu olması gerekmez. **Docker** gerekir (Test ve Helm aşamaları konteynerde koşar, imaj host Docker ile üretilir).

Jenkins job:

1. **New Item** → isim `havadurumu` → **Pipeline**
2. Pipeline tanımı: **Pipeline script from SCM** → Git → bu repo
3. Branch: `*/main` (dalın adı farklıysa düzelt)
4. Script Path: `Jenkinsfile`
5. Save → **Build Now**

Jenkins'i PDF'deki gibi Docker konteynerinde çalıştırıyorsan, pipeline'ın `docker` komutunu görebilmesi için soketi bağla:

```powershell
docker run -d --name jenkins `
  -p 8080:8080 -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts-jdk17
```

Windows Docker Desktop'ta soket yolu farklı olabilir; o zaman Jenkins'i host'ta çalıştırıp Docker'ı PATH'te bırakmak daha basittir.

CI'yı Jenkins olmadan yerelde denemek:

```powershell
py -3.14 -m pip install -r requirements-dev.txt
py -3.14 -m pytest
docker run --rm -v ${PWD}:/src -w /src alpine/helm:3.16.4 lint charts/havadurumu
docker build -t havadurumu:0.1.0 .
```
