pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials'
        DOCKER_IMAGE = "farah16629/myapp"
        CONTAINER_NAME = "myapp"
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
                    echo "Setting up Python and running unit tests..."
                    docker.image('python:3.10').inside('-u root -v ${WORKSPACE}:/workspace -w /workspace') {
                        sh '''
                            set -e
                            echo "=== Upgrading pip and setuptools ==="
                            python3 -m pip install --upgrade pip setuptools wheel

                            echo "=== Installing dependencies ==="
                            if [ -f requirements.txt ]; then
                                pip install -r requirements.txt
                            fi

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
                    echo "🐳 Building and pushing Docker image..."
                    withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS,
                                                      usernameVariable: 'DOCKER_USER',
                                                      passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                            docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker push ${DOCKER_IMAGE}:latest
                            docker logout
                        '''
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                script {
                    echo "Deploying to staging environment..."
                    sh '''
                        echo "=== Cleaning up old staging containers ==="
                        docker compose -f docker-compose.staging.yml down || true
                        echo "=== Starting new staging environment ==="
                        docker compose -f docker-compose.staging.yml up -d --build
                    '''
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    echo "Running integration tests..."
                    sh '''
                        echo "=== Waiting for app to start ==="
                        for i in $(seq 1 10); do
                            if docker exec $(docker ps -qf "name=myapp-staging") curl -s http://localhost:8080 > /dev/null; then
                                echo "App is ready!"
                                break
                            fi
                            echo "Waiting for app... ($i)"
                            sleep 5
                        done

                        echo "=== Running integration tests ==="
                        mkdir -p reports
                        docker run --rm \
                            --network my-ci-cd-project_default \
                            -v $WORKSPACE:/workspace -w /workspace \
                            python:3.10 bash -c "
                                python3 -m pip install -r requirements.txt
                                PYTHONPATH=. pytest tests/integration -q --junitxml=reports/integration.xml
                            "
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "Deploying to production..."
                    sh '''
                        echo "=== Cleaning up old production containers ==="
                        docker compose -f docker-compose.prod.yml down || true
                        echo "=== Starting new production environment ==="
                        docker compose -f docker-compose.prod.yml up -d --build
                    '''
                }
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

        success {
            echo " Pipeline completed successfully!"
        }

        failure {
            echo " Pipeline failed! Please check logs."
        }
    }
}
