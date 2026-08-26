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
            defaultValue: true,
            description: 'Açık olursa imaj ACR’ye yüklenir ve Azure App Service güncellenir.'
        )
    }

    environment {
        APP_NAME             = 'havadurumu'
        RELEASE              = 'bilgeadam'
        CHART                = 'charts/havadurumu'
        IMAGE_REPO           = 'havadurumu'
        IMAGE_TAG            = "0.1.${env.BUILD_NUMBER}"
        PYTHON_CI            = 'python:3.14.7-slim'
        HELM_CI              = 'alpine/helm:3.16.4'
        AZURE_CLI_CI         = 'mcr.microsoft.com/azure-cli:latest'

        // Azure Yapılandırma Bilgileri
        AZURE_RESOURCE_GROUP = 'gokyuzuhava-rg'
        AZURE_ACR_NAME       = 'gokyuzuhavaacr'
        AZURE_APP_NAME       = 'gokyuzuhava-app'

        // Azure Service Principal Kimlik Bilgileri
        AZURE_CLIENT_ID      = 'YOUR_AZURE_CLIENT_ID'
        AZURE_CLIENT_SECRET  = 'YOUR_AZURE_CLIENT_SECRET'
        AZURE_TENANT_ID      = 'YOUR_AZURE_TENANT_ID'
        AZURE_SUBSCRIPTION_ID= 'YOUR_AZURE_SUBSCRIPTION_ID'
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
                    echo "Gökyüzü CI image=${IMAGE_REPO}:${IMAGE_TAG} chart=${CHART}"
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
                    def cmd = "docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -t ${IMAGE_REPO}:latest ."
                    if (isUnix()) {
                        sh cmd
                    } else {
                        bat cmd
                    }
                }
            }
        }

        stage('Deploy Azure App Service') {
            when {
                expression { return params.DEPLOY_AZURE }
            }
            steps {
                script {
                    def acrServer   = "${AZURE_ACR_NAME}.azurecr.io"
                    def fullImage   = "${acrServer}/${IMAGE_REPO}:${IMAGE_TAG}"
                    def latestImage = "${acrServer}/${IMAGE_REPO}:latest"

                    echo "Azure ACR ve App Service dağıtımı başlatılıyor..."
                    echo "Hedef: https://${AZURE_APP_NAME}.azurewebsites.net"

                    if (!env.AZURE_CLIENT_ID?.trim() || env.AZURE_CLIENT_ID == 'YOUR_AZURE_CLIENT_ID') {
                        error('Lütfen Jenkinsfile içindeki AZURE_CLIENT_ID, AZURE_CLIENT_SECRET ve AZURE_TENANT_ID alanlarına kendi Azure bilgilerinizi yazın.')
                    }

                    sh "docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${fullImage}"
                    sh "docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${latestImage}"

                    echo "azure-cli imajı çekiliyor..."
                    sh "docker pull ${AZURE_CLI_CI}"

                    writeFile file: 'reports/azure-login.sh', text: """#!/bin/sh
set -e
echo "az login (service principal)"
az login --service-principal -u "\$AZURE_CLIENT_ID" -p "\$AZURE_CLIENT_SECRET" --tenant "\$AZURE_TENANT_ID" --output none
if [ -n "\${AZURE_SUBSCRIPTION_ID:-}" ]; then
  az account set --subscription "\$AZURE_SUBSCRIPTION_ID" --output none
fi
echo "ACR token"
az acr login --name ${AZURE_ACR_NAME} --expose-token --query accessToken -o tsv
"""

                    writeFile file: 'reports/azure-webapp.sh', text: """#!/bin/sh
set -e
az login --service-principal -u "\$AZURE_CLIENT_ID" -p "\$AZURE_CLIENT_SECRET" --tenant "\$AZURE_TENANT_ID" --output none
if [ -n "\${AZURE_SUBSCRIPTION_ID:-}" ]; then
  az account set --subscription "\$AZURE_SUBSCRIPTION_ID" --output none
fi

echo "Port ayarı yapılıyor (8080)..."
az webapp config appsettings set \\
  --resource-group ${AZURE_RESOURCE_GROUP} \\
  --name ${AZURE_APP_NAME} \\
  --settings WEBSITES_PORT=8080

echo "Kapsayıcı imajı güncelleniyor..."
az webapp config container set \\
  --resource-group ${AZURE_RESOURCE_GROUP} \\
  --name ${AZURE_APP_NAME} \\
  --docker-custom-image-name ${latestImage} \\
  --docker-registry-server-url https://${acrServer}

az webapp restart --resource-group ${AZURE_RESOURCE_GROUP} --name ${AZURE_APP_NAME}
echo CANLI URL: https://${AZURE_APP_NAME}.azurewebsites.net
"""

                    echo "ACR login + docker push..."
                    sh """
                        set -e
                        self=\$(hostname)
                        chmod +x reports/azure-login.sh reports/azure-webapp.sh
                        TOKEN=\$(docker run --rm \\
                          --volumes-from "\$self" \\
                          -w "${env.WORKSPACE}" \\
                          -e AZURE_CLIENT_ID -e AZURE_CLIENT_SECRET -e AZURE_TENANT_ID -e AZURE_SUBSCRIPTION_ID \\
                          --entrypoint sh \\
                          ${AZURE_CLI_CI} \\
                          "${env.WORKSPACE}/reports/azure-login.sh")
                        echo "\$TOKEN" | docker login ${acrServer} --username 00000000-0000-0000-0000-000000000000 --password-stdin
                        docker push ${fullImage}
                        docker push ${latestImage}
                    """

                    echo "App Service güncelleniyor..."
                    sh """
                        set -e
                        self=\$(hostname)
                        docker run --rm \\
                          --volumes-from "\$self" \\
                          -w "${env.WORKSPACE}" \\
                          -e AZURE_CLIENT_ID -e AZURE_CLIENT_SECRET -e AZURE_TENANT_ID -e AZURE_SUBSCRIPTION_ID \\
                          --entrypoint sh \\
                          ${AZURE_CLI_CI} \\
                          "${env.WORKSPACE}/reports/azure-webapp.sh"
                    """
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
                            kubectl wait --namespace ingress-nginx \
                              --for=condition=ready pod \
                              --selector=app.kubernetes.io/component=controller \
                              --timeout=180s || true

                            docker exec minikube minikube image load ${IMAGE_REPO}:${IMAGE_TAG} || true
                            docker exec minikube helm upgrade --install ${RELEASE} ${CHART} --wait --timeout 3m || true
                            docker exec minikube kubectl get pods,svc,ingress -l app=${APP_NAME} || true
                        """
                    } else {
                        bat 'powershell -ExecutionPolicy Bypass -File scripts\\deploy.ps1'
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                echo "============================================================"
                echo " Pipeline Başarıyla Tamamlandı!"
                echo " İmaj Tag: ${IMAGE_REPO}:${IMAGE_TAG}"
                if (params.DEPLOY_AZURE) {
                    echo " Canlı Azure URL: https://${AZURE_APP_NAME}.azurewebsites.net"
                }
                echo "============================================================"
            }
        }
        failure {
            echo "Pipeline hata aldı. Detaylar için Build Console Log'unu inceleyin."
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
        if ! docker info >/dev/null 2>&1; then
          echo "Docker socket erişilemiyor."
          exit 1
        fi
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