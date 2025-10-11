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
sh '''
docker stop my-ci-cd-pipeline_prometheus_1 || echo "No container found"
docker rm my-ci-cd-pipeline_prometheus_1 || echo "Already removed"
docker-compose -f docker-compose.staging.yml up -d --build
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
