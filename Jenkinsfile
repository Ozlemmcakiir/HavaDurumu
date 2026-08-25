pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 25, unit: 'MINUTES')
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
        string(name: 'AZURE_RESOURCE_GROUP', defaultValue: '', description: 'azure-setup.ps1 betiğinden gelen AZURE_RESOURCE_GROUP')
        string(name: 'AZURE_ACR_NAME', defaultValue: '', description: 'azure-setup.ps1 betiğinden gelen AZURE_ACR_NAME')
        string(name: 'AZURE_APP_NAME', defaultValue: '', description: 'azure-setup.ps1 betiğinden gelen AZURE_APP_NAME')
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
                        error('DEPLOY_AZURE açık ama AZURE_RESOURCE_GROUP / AZURE_ACR_NAME / AZURE_APP_NAME boş. Build with Parameters ile azure-setup.ps1 çıktısını yazın. Canlı URL: https://<AZURE_APP_NAME>.azurewebsites.net')
                    }
                    echo "Azure hedef: https://${app}.azurewebsites.net  RG=${rg} ACR=${acr}"

                    if (isUnix()) {
                        sh '''
                            set -e
                            echo "HEAD=$(git rev-parse --short HEAD 2>/dev/null || true)"
                            pwd
                            mkdir -p scripts
                            if [ ! -f scripts/deploy-azure.sh ]; then
                              echo "deploy-azure.sh workspace'te yok; GitHub main aliniyor"
                              curl -fsSL https://raw.githubusercontent.com/Ozlemmcakiir/HavaDurumu/main/scripts/deploy-azure.sh -o scripts/deploy-azure.sh
                            fi
                            # Windows checkout CRLF kirarsa sh hata verir
                            sed -i 's/\r$//' scripts/deploy-azure.sh 2>/dev/null || sed -i '' 's/\r$//' scripts/deploy-azure.sh
                            chmod +x scripts/deploy-azure.sh
                            ls -la scripts/deploy-azure.sh
                        '''
                        sh "sh scripts/deploy-azure.sh '${rg}' '${acr}' '${app}'"
                    } else {
                        if (!fileExists('scripts/deploy-azure.ps1')) {
                            error('scripts/deploy-azure.ps1 yok. Jenkins Git branch: main, son commit çekilsin.')
                        }
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
                if (params.DEPLOY_AZURE && params.AZURE_APP_NAME?.trim()) {
                    echo "CANLI site (Azure): https://${params.AZURE_APP_NAME}.azurewebsites.net"
                }
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