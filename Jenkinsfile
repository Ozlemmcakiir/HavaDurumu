pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 40, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    parameters {
        booleanParam(
            name: 'DEPLOY_MINIKUBE',
            defaultValue: false,
            description: 'Açık olursa Minikube + Helm + nginx Ingress kurulur.'
        )
        booleanParam(
            name: 'DEPLOY_AZURE',
            defaultValue: false,
            description: 'Açık olursa Azure Container Registry (ACR) ve App Service üzerine canlıya alma yapılır.'
        )
        string(name: 'AZURE_RESOURCE_GROUP', defaultValue: 'havadurumu-rg', description: 'Azure resource group')
        string(name: 'AZURE_ACR_NAME', defaultValue: '', description: 'Azure Container Registry adı (azure-setup çıktısı)')
        string(name: 'AZURE_APP_NAME', defaultValue: 'gokyuzu-app', description: 'Canlı site: https://gokyuzu-app.azurewebsites.net')
    }

    environment {
        APP_NAME   = 'havadurumu'
        RELEASE    = 'bilgeadam'
        CHART      = 'charts/havadurumu'
        IMAGE_REPO = 'havadurumu'
        IMAGE_TAG  = "0.1.${env.BUILD_NUMBER}"
        PYTHON_CI  = 'python:3.14.7-slim'
        HELM_CI    = 'alpine/helm:3.16.4'
    }

    stages {

        stage('Checkout') {
            steps {
                script {
                    try {
                        checkout scm
                    } catch (err) {
                        echo "SCM bağlı değil. Public Git reposu klonlanıyor..."
                        git branch: 'main', url: 'https://github.com/Ozlemmcakiir/HavaDurumu.git'
                    }
                    echo "Gökyüzü CI  image=${IMAGE_REPO}:${IMAGE_TAG}  chart=${CHART}"
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    dockerSh("${PYTHON_CI}", "sh scripts/ci-test.sh")
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Helm Lint') {
            steps {
                script {
                    dockerSh("${HELM_CI}", "lint ${CHART}")
                    dockerSh("${HELM_CI}", "template ${RELEASE} ${CHART}")
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    def cmd = "docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -t ${IMAGE_REPO}:0.1.0 ."
                    if (isUnix()) {
                        sh cmd
                    } else {
                        bat cmd
                    }
                }
            }
        }

        stage('Deploy Minikube') {
            when {
                expression { return params.DEPLOY_MINIKUBE }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            set -e
                            minikube addons enable ingress || true
                            kubectl wait --namespace ingress-nginx \\
                              --for=condition=ready pod \\
                              --selector=app.kubernetes.io/component=controller \\
                              --timeout=180s || true

                            docker exec minikube minikube image load ${IMAGE_REPO}:0.1.0 || true
                            docker exec minikube helm upgrade --install ${RELEASE} ${CHART} --wait --timeout 3m || true
                            docker exec minikube kubectl get pods,svc,ingress -l app=${APP_NAME} || true
                        """
                    } else {
                        bat 'powershell -ExecutionPolicy Bypass -File scripts\\deploy.ps1'
                    }
                }
            }
        }

        stage('Deploy Azure') {
            when {
                expression { return params.DEPLOY_AZURE }
            }
            steps {
                script {
                    def rg  = params.AZURE_RESOURCE_GROUP?.trim()
                    def acr = params.AZURE_ACR_NAME?.trim()
                    def app = params.AZURE_APP_NAME?.trim()
                    if (!rg || !acr || !app) {
                        error('DEPLOY_AZURE açık ama AZURE_RESOURCE_GROUP / AZURE_ACR_NAME / AZURE_APP_NAME boş. Canlı URL: https://gokyuzu-app.azurewebsites.net')
                    }
                    echo "Azure hedef: https://gokyuzu-app.azurewebsites.net  RG=${rg} ACR=${acr} APP=${app}"

                    // Harici .sh dosyası yoksa da çalışsın (eski workspace / SCM kayması).
                    if (isUnix()) {
                        sh """
                            set -e
                            command -v az >/dev/null || { echo 'Azure CLI yok. Agent: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash'; exit 1; }
                            command -v docker >/dev/null || { echo 'Docker yok.'; exit 1; }

                            RG='${rg}'
                            ACR='${acr}'
                            APP='${app}'
                            LOCAL='${IMAGE_REPO}:${IMAGE_TAG}'
                            REMOTE='${acr}.azurecr.io/havadurumu:${IMAGE_TAG}'
                            LATEST='${acr}.azurecr.io/havadurumu:0.1.0'

                            if [ -n "\$AZURE_CLIENT_ID" ] && [ -n "\$AZURE_CLIENT_SECRET" ] && [ -n "\$AZURE_TENANT_ID" ]; then
                              az login --service-principal -u "\$AZURE_CLIENT_ID" -p "\$AZURE_CLIENT_SECRET" --tenant "\$AZURE_TENANT_ID" --output none
                              [ -n "\$AZURE_SUBSCRIPTION_ID" ] && az account set --subscription "\$AZURE_SUBSCRIPTION_ID" --output none
                            else
                              az account show --output none || { echo 'Jenkins env: AZURE_CLIENT_ID SECRET TENANT_ID ekleyin'; exit 1; }
                            fi

                            docker image inspect "\$LOCAL" >/dev/null
                            az acr login --name "\$ACR"
                            docker tag "\$LOCAL" "\$REMOTE"
                            docker tag "\$LOCAL" "\$LATEST"
                            docker push "\$REMOTE"
                            docker push "\$LATEST"
                            az webapp config container set --name "\$APP" --resource-group "\$RG" --docker-custom-image-name "\$REMOTE" --output none
                            az webapp restart --name "\$APP" --resource-group "\$RG" --output none
                            echo CANLI URL: https://gokyuzu-app.azurewebsites.net
                        """
                    } else {
                        bat "powershell -ExecutionPolicy Bypass -File scripts\\deploy-azure.ps1 -ResourceGroup '${rg}' -AcrName '${acr}' -AppName '${app}'"
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                echo "Pipeline yeşil. İmaj: ${IMAGE_REPO}:${IMAGE_TAG}"
                echo "CANLI site: https://gokyuzu-app.azurewebsites.net"
            }
        }
        failure {
            echo "Pipeline kırıldı. Console Output'un en altına bak."
        }
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}

def dockerSh(String image, String innerCommand) {
    if (!isUnix()) {
        def vol = env.WORKSPACE.replace('\\', '/')
        bat "docker run --rm -v \"${vol}:/src\" -w /src ${image} ${innerCommand}"
        return
    }

    sh """
        set -e
        mkdir -p reports
        self=\$(hostname)
        if [ -f /.dockerenv ] && docker inspect "\$self" >/dev/null 2>&1; then
          docker run --rm --volumes-from "\$self" -w "${env.WORKSPACE}" ${image} ${innerCommand}
        elif [ ! -f /.dockerenv ]; then
          docker run --rm -v "${env.WORKSPACE}:/src" -w /src ${image} ${innerCommand}
        else
          cid=\$(docker create -w /src ${image} ${innerCommand})
          docker cp "${env.WORKSPACE}/." "\$cid":/src
          set +e
          docker start -a "\$cid"
          rc=\$?
          set -e
          docker cp "\$cid":/src/reports/. "${env.WORKSPACE}/reports/" 2>/dev/null || true
          docker rm -f "\$cid" >/dev/null
          exit \$rc
        fi
    """
}