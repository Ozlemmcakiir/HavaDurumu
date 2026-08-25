# Gökyüzü — Hava Durumu

Open-Meteo verisiyle çalışan Flet web uygulaması. Yerel kümede **Jenkins → Minikube + Helm + nginx Ingress** ile açılır. Satın alınmış domain / A kaydı yok; demo host ücretsizdir.

```
Python kodu → Jenkins (test, helm lint, docker build, deploy)
            → Docker imajı (havadurumu:0.1.0)
            → Helm chart (havadurumu)  release: bilgeadam
            → 2 pod + Service + nginx Ingress
            → http://havadurumu.localtest.me:8080
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
├── Jenkinsfile             # test → helm lint → docker build → (opsiyonel) nginx deploy
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
│       └── ingress.yaml    # nginx: havadurumu.localtest.me
├── k8s/havadurumu.yaml     # Helm öncesi düz YAML (referans)
└── scripts/
    ├── deploy.ps1          # minikube + nginx ingress + helm install
    ├── open-demo.ps1       # nginx'i :8080'e bağlar, demo URL açılır
    ├── uninstall.ps1
    └── ci-test.sh          # Jenkins Test stage (python:3.14.7-slim içinde)
```

## Minikube + Helm (önerilen)

Önkoşul: Docker Desktop ayakta, `minikube` ve `helm` PATH'te (`%USERPROFILE%\bin` yeterli).

Proje kökünden:

```powershell
.\scripts\deploy.ps1
```

Script şunları yapar:

1. Minikube yoksa `minikube start --driver=docker`
2. nginx Ingress addon'u açar, controller hazır olana kadar bekler
3. `minikube image build -t havadurumu:0.1.0 .` — imaj kümenin Docker'ına gider (`imagePullPolicy: Never`)
4. `helm lint charts/havadurumu`
5. `helm upgrade --install bilgeadam charts/havadurumu`

Uygulamayı **nginx üzerinden** açmak (ayrı pencere, açık kalsın):

```powershell
.\scripts\open-demo.ps1
```

Tarayıcı: [http://havadurumu.localtest.me:8080](http://havadurumu.localtest.me:8080) — varsayılan şehir Ankara.

`localtest.me` ücretsiz bir demo DNS'tir, `127.0.0.1`'e gider. Domain satın almaya ve A kaydı girmeye gerek yoktur. Hosts dosyası da gerekmez.

Akış: tarayıcı → nginx Ingress → Service `havadurumu:8000` → Flet pod.

Adım adım elle:

```powershell
minikube start --driver=docker
minikube addons enable ingress
minikube image build -t havadurumu:0.1.0 .
helm upgrade --install bilgeadam charts/havadurumu
kubectl get pods,svc,ingress -l app=havadurumu
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
```

Tarayıcı: [http://havadurumu.localtest.me:8080](http://havadurumu.localtest.me:8080)

### Sık komutlar

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
docker run --rm -p 8080:8000 havadurumu:0.1.0
```

Konteyner 8000 dinler; laptop'ta 8080'e map edilir.

## Jenkins CI

Kod Git'e düşünce (veya Jenkins'te **Build Now**) sırayla:

1. **Test** — `python:3.14.7-slim` içinde `py_compile` + pytest (Open-Meteo çağrıları mock'lanır, internet gerekmez)
2. **Helm Lint** — `alpine/helm` ile `helm lint` + `helm template`
3. **Docker Build** — `havadurumu:0.1.<BUILD_NUMBER>` ve `havadurumu:0.1.0`
4. **Deploy Minikube** — kapalı gelir; job parametresinde `DEPLOY_MINIKUBE` işaretlenirse nginx Ingress açılır, Helm ile `bilgeadam` kurulur. Sonra `.\scripts\open-demo.ps1` → [http://havadurumu.localtest.me:8080](http://havadurumu.localtest.me:8080)

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
