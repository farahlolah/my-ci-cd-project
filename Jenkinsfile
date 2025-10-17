pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKER_IMAGE = "farah16629/myapp"
        STAGING_COMPOSE = "docker-compose.staging.yml"
        PROD_COMPOSE = "docker-compose.prod.yml"
        NETWORK_NAME = "my-ci-cd-pipeline-net"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests (Inside Docker)') {
            steps {
                script {
                    echo "Running unit tests inside Docker image..."
                    sh '''
                        docker build -t $DOCKER_IMAGE:test -f Dockerfile .
                        docker run --rm -v $(pwd):/app $DOCKER_IMAGE:test \
                            bash -c "pytest tests/unit -q --junitxml=reports/unit.xml"
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/unit.xml'
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    echo "Building and pushing Docker image..."
                    sh '''
                        docker build -t $DOCKER_IMAGE:staging -f Dockerfile .
                        echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin
                        docker push $DOCKER_IMAGE:staging
                    '''
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                script {
                    echo "Deploying to staging environment..."
                    sh '''
                        docker compose -f ${STAGING_COMPOSE} down || true
                        docker compose -f ${STAGING_COMPOSE} up -d --build
                    '''
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    echo "Running integration tests..."
                    sh '''
                        docker run --rm -v $(pwd):/app $DOCKER_IMAGE:staging \
                            bash -c "pytest tests/integration -q --junitxml=reports/integration.xml"
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/integration.xml'
                }
            }
        }

        stage('Deploy to Production') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                script {
                    echo "Deploying to production..."
                    sh '''
                        docker compose -f ${PROD_COMPOSE} down || true
                        docker compose -f ${PROD_COMPOSE} up -d --build
                    '''
                }
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed! Check the logs above."
        }
        success {
            echo "Pipeline completed successfully!"
        }
    }
}
