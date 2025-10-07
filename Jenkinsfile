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
            }
        }

        stage('Install & Unit Tests') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root'
                }
            }
            steps {
                echo "Installing dependencies and running unit tests..."
                sh '''
                    echo "=== Checking directory contents ==="
                    pwd
                    ls -R
                    echo "=== Installing dependencies ==="
                    python3 -m pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    echo "=== Running unit tests ==="
                    mkdir -p reports
                    PYTHONPATH=. pytest tests/unit -q --junitxml=reports/unit.xml
                '''
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
                        img.push('staging')
                    }
                }
            }
        }

stage('Deploy to Staging') {
    steps {
        echo "=== Cleaning up old containers and network ==="
        powershell '''
            # Stop and remove old containers safely
            Write-Host "Stopping and removing old containers..."
            
            docker stop my-ci-cd-pipeline_app_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No app container found" }

            docker rm my-ci-cd-pipeline_app_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "App container already removed" }

            docker stop prometheus 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No prometheus container found" }

            docker rm prometheus 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "Prometheus container already removed" }

            docker stop my-ci-cd-pipeline_prometheus_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No secondary prometheus container found" }

            docker rm my-ci-cd-pipeline_prometheus_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "Secondary Prometheus container already removed" }

            # Remove possible leftover networks
            docker network rm my-ci-cd-pipeline_default 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No default network found" }

            docker network rm my-ci-cd-pipeline_my-ci-cd-pipeline_default 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No secondary network found" }

            # Ensure prometheus.yml exists in workspace
            Write-Host "=== Checking for prometheus.yml ==="
            if (Test-Path "./prometheus.yml") {
                Write-Host "prometheus.yml already exists, skipping copy."
            } else {
                Copy-Item "C:\\Users\\Default.DESKTOP-ROGCKJH\\Downloads\\my-ci-cd-project\\prometheus.yml" "./prometheus.yml"
                Write-Host "Copied prometheus.yml to working directory."
            }

            # Start staging environment
            Write-Host "=== Starting new staging environment ==="
            docker-compose -f docker-compose.staging.yml up -d --build

            # Wait briefly for services to boot
            Start-Sleep -Seconds 5

            # Show running containers
            Write-Host "=== Running containers ==="
            docker ps
        '''
    }
}



        stage('Integration Tests') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root'
                }
            }
            steps {
                echo "Running integration tests..."
                sh '''
                    mkdir -p reports
                    PYTHONPATH=. pytest tests/integration -q --junitxml=reports/integration.xml
                '''
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
            echo "Archiving test reports..."
            junit 'reports/**/*.xml'
        }
        failure {
            mail to: 'farahwael158@gmail.com',
                 subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                 body: "Build failed. View details here: ${env.BUILD_URL}"
        }
    }
}
