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
                        echo '=== Checking directory contents ===' &&
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
                    withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DOCKERHUB_USERNAME', passwordVariable: 'DOCKERHUB_PASSWORD')]) {
                        sh '''
                            echo "=== Building Docker image ==="
                            docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest my-ci-cd-pipeline

                            echo "=== Logging into DockerHub ==="
                            echo "${DOCKERHUB_PASSWORD}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin

                            echo "=== Pushing Docker image to DockerHub ==="
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker push ${DOCKER_IMAGE}:latest

                            echo "=== Logout from DockerHub ==="
                            docker logout
                        '''
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    docker-compose -f docker-compose.staging.yml up -d
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
    }
}
