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
            description: 'Açık olursa Minikube + Helm ile bilgeadam release kurulur. Agent bu makinede minikube/helm görmeli.'
        )
    }

    environment {
        APP_NAME   = 'havadurumu'
        RELEASE    = 'bilgeadam'
        CHART      = 'charts/havadurumu'
        IMAGE_REPO = 'havadurumu'
        IMAGE_TAG  = "0.1.${env.BUILD_NUMBER}"
        PYTHON_CI  = 'python:3.12-slim'
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
                            export PATH="\$HOME/bin:\$PATH"
                            minikube image build -t ${IMAGE_REPO}:0.1.0 .
                            helm upgrade --install ${RELEASE} ${CHART} --wait --timeout 3m
                            kubectl get pods,svc -l app=${APP_NAME}
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
            echo "Pipeline yeşil. İmaj: ${IMAGE_REPO}:${IMAGE_TAG}"
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
    def vol = env.WORKSPACE
    if (!isUnix()) {
        vol = vol.replace('\\', '/')
    }
    def line = "docker run --rm -v \"${vol}:/src\" -w /src ${image} ${innerCommand}"
    if (isUnix()) {
        sh line
    } else {
        bat line
    }
}