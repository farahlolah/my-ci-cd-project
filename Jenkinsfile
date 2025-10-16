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
            steps {
                script {
                    // Convert Windows path to Unix-style (for Docker compatibility)
                    def workspaceUnix = bat(
                        script: 'cygpath "${WORKSPACE}"',
                        returnStdout: true
                    ).trim()

                    docker.image('python:3.10').inside("-u root -v ${workspaceUnix}:/workspace -w /workspace") {
                        sh '''
                            echo "=== Installing dependencies and running unit tests ==="
                            python3 -m pip install --upgrade pip setuptools wheel

                            echo "=== Checking directory contents ==="
                            pwd
                            ls -R

                            # Install app dependencies
                            if [ -f requirements.txt ]; then
                                pip install -r requirements.txt
                            else
                                echo "No requirements.txt found — installing Flask manually"
                                pip install flask
                            fi

                            # Install test dependencies
                            if [ -f tests/requirements.txt ]; then
                                pip install -r tests/requirements.txt
                            fi

                            # Ensure pytest is available even if requirements.txt missing
                            pip install pytest --upgrade

                            echo "=== Running unit tests ==="
                            mkdir -p reports
                            PYTHONPATH=. pytest tests/unit -q --junitxml=reports/unit.xml
                        '''
                    }
                }
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
                script {
                    echo "=== Cleaning up old containers and network ==="

                    if (isUnix()) {
                        sh '''
                            docker stop my-ci-cd-pipeline_prometheus_1 || true
                            docker rm my-ci-cd-pipeline_prometheus_1 || true
                            docker stop my-ci-cd-pipeline_app_1 || true
                            docker rm my-ci-cd-pipeline_app_1 || true
                            docker network rm my-ci-cd-pipeline_default || true

                            echo "=== Starting staging environment with docker-compose ==="
                            docker-compose -f docker-compose.staging.yml up -d --build
                        '''
                    } else {
                        powershell '''
                            Write-Host "=== Cleaning up old containers and network ==="
                            docker stop my-ci-cd-pipeline_prometheus_1 2>$null
                            if ($LASTEXITCODE -ne 0) { Write-Host "No Prometheus container found" }
                            docker rm my-ci-cd-pipeline_prometheus_1 2>$null
                            if ($LASTEXITCODE -ne 0) { Write-Host "Prometheus container already removed" }

                            docker stop my-ci-cd-pipeline_app_1 2>$null
                            if ($LASTEXITCODE -ne 0) { Write-Host "No App container found" }
                            docker rm my-ci-cd-pipeline_app_1 2>$null
                            if ($LASTEXITCODE -ne 0) { Write-Host "App container already removed" }

                            docker network rm my-ci-cd-pipeline_default 2>$null
                            if ($LASTEXITCODE -ne 0) { Write-Host "No default network found" }

                            Write-Host "=== Starting staging environment with docker-compose ==="
                            docker-compose -f docker-compose.staging.yml up -d --build
                        '''
                    }
                }
            }
        }

        stage('Integration Tests') {
            steps {
                echo "Running integration tests inside staging network..."
                sh '''
                    echo "=== Running integration tests ==="
                    mkdir -p reports

                    echo "=== Waiting for app to start ==="
                    for i in $(seq 1 20); do
                        if docker exec my-ci-cd-pipeline_app_1 curl -s http://localhost:8080/metrics > /dev/null; then
                            echo "App is ready!"
                            break
                        fi
                        echo "Waiting for app... ($i)"
                        sleep 2
                    done

                    echo "=== Running integration tests ==="
                    docker run --rm \
                        --network my-ci-cd-pipeline_default \
                        -v $WORKSPACE:/workspace -w /workspace \
                        python:3.10 bash -c "
                            echo '=== Checking files inside container ==='
                            ls -l /workspace
                            python3 -m pip install --upgrade pip setuptools wheel
                            pip install flask pytest
                            if [ -f tests/requirements.txt ]; then pip install -r tests/requirements.txt; fi
                            PYTHONPATH=. pytest tests/integration -q --junitxml=reports/integration.xml
                        "
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
            script {
                if (fileExists('reports')) {
                    echo "Archiving test reports..."
                    junit 'reports/**/*.xml'
                } else {
                    echo "No test reports found. Skipping JUnit archiving."
                }
            }
        }

        failure {
            echo "Build failed. Email notification skipped (SMTP not configured)."
        }
    }
}
