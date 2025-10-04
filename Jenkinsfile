pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials'
        DOCKER_IMAGE = "farah16629/myapp"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                git branch: 'main', url: 'https://github.com/farahlolah/my-ci-cd-project.git'
                sh 'echo "Checkout listing:" && ls -la'
            }
        }

        stage('Install & Unit Tests') {
            steps {
                echo "Running unit tests inside Python container (mounting jenkins_home volume)..."
                script {
                    def jobWorkspace = "workspace/my-ci-cd-pipeline"
                    sh """
                        echo "=== Host-side workspace (Jenkins) path ==="
                        echo "/var/jenkins_home/${jobWorkspace}"
                        echo "=== Listing workspace on Jenkins host side (inside Jenkins container) ==="
                        ls -la /var/jenkins_home/${jobWorkspace} || true

                        echo "=== Starting python container mounting named volume 'jenkins_home' ==="
                        docker run --rm \
                            -v jenkins_home:/data \
                            -w /data/${jobWorkspace} \
                            python:3.10 bash -c '
                                echo \"=== Inside test container: pwd ===\" &&
                                pwd &&
                                echo \"=== Inside test container: listing files ===\" &&
                                ls -la ||
                                ( echo \"Workspace empty inside container\" && exit 2 ) &&
                                echo \"=== Upgrading pip and installing dependencies ===\" &&
                                python3 -m pip install --upgrade pip setuptools wheel &&
                                pip install -r requirements.txt &&
                                mkdir -p reports &&
                                PYTHONPATH=. pytest tests/unit -q --junitxml=reports/unit.xml
                            '
                    """
                }
            }
        }

        stage('Static Analysis') {
            steps {
                echo "Skipping static analysis (placeholder stage)..."
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    echo "Building and pushing Docker image to DockerHub..."
                    docker.withRegistry('', DOCKERHUB_CREDENTIALS) {
                        def img = docker.build("${env.DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                        img.push()
                        img.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    docker-compose -f docker-compose.staging.yml up -d --build
                    sleep 5
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                echo "Running integration tests..."
                sh 'PYTHONPATH=. pytest tests/integration -q --junitxml=reports/integration.xml'
            }
        }

        stage('Deploy to Production') {
            steps {
                echo "Deploying to production environment..."
                sh 'docker-compose -f docker-compose.prod.yml up -d'
            }
        }
    }

    post {
        always {
            echo "Archiving reports..."
            junit 'reports/**/*.xml'
        }
        failure {
            mail to: 'farahwael158@gmail.com',
                 subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                 body: "Jenkins build failed. Check details: ${env.BUILD_URL}"
        }
    }
}
