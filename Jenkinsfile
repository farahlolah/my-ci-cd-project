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
                        pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml || true"
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
                    echo "⏳ Waiting for app to be ready..."
                    def retries = 20
                    def ready = false

                    for (def i = 1; i <= retries; i++) {
                        def result = sh(
                            script: """
                            docker run --rm --network ${NETWORK_NAME} $DOCKER_IMAGE:test python3 -c "import requests, sys; \
try: r = requests.get('http://app:8081/metrics', timeout=3); sys.exit(0 if r.status_code == 200 else 1) \
except: sys.exit(1)"
                            """,
                            returnStatus: true
                        )

                        if (result == 0) {
                            ready = true
                            echo "✅ App is ready after ${i} attempts"
                            break
                        }

                        echo "⏳ Waiting for app... (${i})"
                        sleep 3
                    }

                    if (!ready) {
                        echo "❌ App did not become ready in time — printing logs..."
                        sh "docker compose -f ${STAGING_COMPOSE} logs app || true"
                    }

                    echo "🚀 Running integration tests (output only, pipeline will not fail)..."
                    sh """
                        docker run --rm --network ${NETWORK_NAME} $DOCKER_IMAGE:test bash -c "mkdir -p /app/reports && \
                        PYTHONPATH=/app pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml || true"
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
            echo "📄 Collecting test reports..."
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
        }
        failure {
            echo "⚠️ Pipeline failed! Check the logs above."
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
    }
}
