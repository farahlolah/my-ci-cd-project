pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "farah16629/myapp"
        STAGING_COMPOSE = "docker-compose.staging.yml"
        PROD_COMPOSE = "docker-compose.prod.yml"
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
                    // Secure Docker login with credentials stored in Jenkins
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
                    echo "🔍 Waiting for app to be ready..."
                    sh "sleep 5"

                    // Detect actual network created by docker-compose (e.g., thesis_default)
                    def networkName = sh(
                        script: "docker network ls --format '{{.Name}}' | grep thesis_default || true",
                        returnStdout: true
                    ).trim()

                    if (!networkName) {
                        error("❌ Could not find docker network (thesis_default). Check docker-compose output.")
                    }

                    echo "✅ Using network: ${networkName}"

                    // Run integration tests inside the same network as app
                    sh """
                        docker run --rm --network ${networkName} $DOCKER_IMAGE:test bash -c "
                            mkdir -p /app/reports && \
                            PYTHONPATH=/app pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml
                        "
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
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
        }
        failure {
            echo "❌ Pipeline failed! Check the logs above."
        }
        success {
            echo "🎉 Pipeline completed successfully!"
        }
    }
}
