pipeline {
    agent any

    environment {
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
                    sh """
                        docker build -t $DOCKER_IMAGE:test -f Dockerfile .
                        docker run --rm -w /app $DOCKER_IMAGE:test bash -c "mkdir -p /app/reports && \
                        pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml"
                    """
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    withDockerRegistry([credentialsId: 'dockerhub-credentials', url: 'https://index.docker.io/v1/']) {
                        sh """
                            docker build -t $DOCKER_IMAGE:latest -f Dockerfile .
                            docker push $DOCKER_IMAGE:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh """
                    docker compose -f ${STAGING_COMPOSE} down || true
                    docker compose -f ${STAGING_COMPOSE} up -d --build
                """
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    echo "Running integration tests..."
                    sh """
                        docker run --rm --network ${NETWORK_NAME} $DOCKER_IMAGE:test bash -c '
                            echo "Waiting for app...";
                            for i in \$(seq 1 20); do
                                curl -s http://app:8080/metrics && break || { echo "Waiting..." && sleep 3; }
                            done;
                            PYTHONPATH=/app pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml
                        '
                    """
                }
            }
        }

        stage('Deploy to Production') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh """
                    docker compose -f ${PROD_COMPOSE} down || true
                    docker compose -f ${PROD_COMPOSE} up -d --build
                """
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/*.xml', healthScaleFactor: 0.0, skipPublishingChecks: true
        }
        failure {
            echo "Pipeline failed! Check the logs above."
        }
        success {
            echo "Pipeline completed successfully!"
        }
    }
}
