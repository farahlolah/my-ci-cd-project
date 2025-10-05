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
                    echo "=== Running inside Python container ==="
                    docker run --rm -v $WORKSPACE:/app -w /app/my-ci-cd-pipeline python:3.10 bash -c "
                        echo '=== Checking directory contents ==='
                        ls -R &&
                        python3 -m pip install --upgrade pip setuptools wheel &&
                        pip install -r requirements.txt &&
                        mkdir -p /app/my-ci-cd-pipeline/reports &&
                        PYTHONPATH=. pytest tests/unit -q --junitxml=/app/my-ci-cd-pipeline/reports/unit.xml
                    "
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
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    echo "Cleaning up any old network or containers..."
                    docker stop my-ci-cd-pipeline_app_1 || true
                    docker rm my-ci-cd-pipeline_app_1 || true
                    docker stop my-ci-cd-pipeline_prometheus_1 || true
                    docker rm my-ci-cd-pipeline_prometheus_1 || true
                    docker network rm my-ci-cd-pipeline_default || true

                    echo "prometheus.yml already exists — skipping copy."
                    ls -l prometheus.yml

                    echo "Starting new staging environment..."
                    docker-compose -f docker-compose.staging.yml up -d --build
                    sleep 5
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                echo "Running integration tests..."
                sh '''
                    docker run --rm -v $WORKSPACE:/app -w /app/my-ci-cd-pipeline python:3.10 bash -c "
                        PYTHONPATH=. pytest tests/integration -q --junitxml=/app/my-ci-cd-pipeline/reports/integration.xml
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
            echo "Archiving test reports..."
            junit 'my-ci-cd-pipeline/reports/**/*.xml'
            junit 'reports/**/*.xml'
        }
        failure {
            mail to: 'farahwael158@gmail.com',
                 subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                 body: "Build failed. View details here: ${env.BUILD_URL}"
        }
    }
}
