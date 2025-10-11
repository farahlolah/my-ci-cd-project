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
                    args '-u root -v $WORKSPACE:/workspace -w /workspace'
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
        echo "=== Deploying to Staging Environment (PowerShell compatible) ==="
        powershell '''
            Write-Host "=== Cleaning up old containers and network ==="

            # Stop and remove old app container
            docker stop my-ci-cd-pipeline_app_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No app container found" }

            docker rm my-ci-cd-pipeline_app_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "App container already removed" }

            # Stop and remove old Prometheus container
            docker stop my-ci-cd-pipeline_prometheus_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No Prometheus container found" }

            docker rm my-ci-cd-pipeline_prometheus_1 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "Prometheus container already removed" }

            # Remove any networks related to the project
            docker network rm my-ci-cd-pipeline_default 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No default network found" }

            docker network rm my-ci-cd-project_my-ci-cd-pipeline-net 2>$null
            if ($LASTEXITCODE -ne 0) { Write-Host "No secondary network found" }

            # Double cleanup — remove any leftover containers matching project name
            Write-Host "=== Checking for stray containers ==="
            $containers = docker ps -aq --filter "name=my-ci-cd-pipeline"
            if ($containers) {
                Write-Host "Removing leftover containers..."
                $containers | ForEach-Object { docker rm -f $_ }
            } else {
                Write-Host "No leftover containers found."
            }

            # Start fresh staging environment
            Write-Host "=== Starting new staging environment ==="
            docker-compose -f "C:\\Users\\Default.DESKTOP-ROGCKJH\\Downloads\\my-ci-cd-project\\docker-compose.staging.yml" up -d --build

            Write-Host "=== Waiting for containers to start ==="
            Start-Sleep -Seconds 5

            Write-Host "=== Listing running containers ==="
            docker ps
        '''
    }
}


        stage('Integration Tests') {
            steps {
                echo "Running integration tests..."
                sh '''
                    echo "=== Preparing for integration tests ==="
                    mkdir -p reports

                    echo "=== Waiting for app to start ==="
                    for i in $(seq 1 20); do
                        if docker exec my-ci-cd-pipeline_app_1 curl -s http://localhost:8080/metrics > /dev/null; then
                            echo "App is up!"
                            break
                        fi
                        echo "Waiting for app... ($i)"
                        sleep 2
                    done

                    echo "=== Running integration tests ==="
                    docker run --rm --network my-ci-cd-pipeline_default \
                        -v /var/jenkins_home/workspace/my-ci-cd-pipeline:/workspace \
                        -w /workspace/my-ci-cd-pipeline \
                        python:3.10 bash -c "
                            echo '=== Checking files inside container ==='
                            ls -R /workspace
                            python3 -m pip install --upgrade pip setuptools wheel
                            pip install -r /workspace/requirements.txt
                            PYTHONPATH=/workspace pytest tests/integration -q --junitxml=/workspace/reports/integration.xml
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
            // Uncomment and configure SMTP if needed:
            // mail to: 'farahwael158@gmail.com',
            //      subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
            //      body: "Build failed. View details here: ${env.BUILD_URL}"
        }
    }
}
