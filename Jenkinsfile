pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKER_IMAGE = "farah16629/myapp"
        STAGING_COMPOSE = "docker-compose.staging.yml"
        PROD_COMPOSE = "docker-compose.prod.yml"
        NETWORK_NAME = "my-ci-cd-pipeline-net"
        REPORTS_DIR = "reports"
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
                    sh """
                        mkdir -p ${REPORTS_DIR}
                        docker build -t $DOCKER_IMAGE:test -f Dockerfile .
                        docker run --rm -v "\$(pwd)/${REPORTS_DIR}:/app/reports" -w /app $DOCKER_IMAGE:test \
                            bash -c "pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml"
                    """
                }
                // Publish results tied to this stage
                junit allowEmptyResults: true, testResults: "${REPORTS_DIR}/unit.xml"
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    echo "Building and pushing Docker image..."
                    sh """
                        docker build -t $DOCKER_IMAGE:latest -f Dockerfile .
                        echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin
                        docker push $DOCKER_IMAGE:latest
                    """
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                script {
                    echo "Deploying to staging..."
                    sh """
                        docker compose -f ${STAGING_COMPOSE} down || true
                        docker compose -f ${STAGING_COMPOSE} up -d --build
                    """
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    echo "=== Waiting for app to be ready ==="
                    def retries = 20
                    def ready = false

                    for (i = 1; i <= retries; i++) {
                        def appId = sh(script: "docker ps -qf name=my-ci-cd-pipeline_app_1", returnStdout: true).trim()
                        if (appId) {
                            def result = sh(script: "docker exec ${appId} curl -s http://localhost:8081/metrics || true", returnStdout: true).trim()
                            if (result) {
                                ready = true
                                echo "App is ready after ${i} attempts"
                                break
                            }
                        }
                        echo "Waiting for app... (${i})"
                        sleep 3
                    }

                    if (!ready) {
                        echo "App failed to start. Showing logs..."
                        sh "docker logs \$(docker ps -qf name=my-ci-cd-pipeline_app_1 || true)"
                        error("App did not become ready in time.")
                    }

                    echo "Running integration tests..."
                    sh """
                        docker run --rm --network ${NETWORK_NAME} -v "\$(pwd)/${REPORTS_DIR}:/app/reports" $DOCKER_IMAGE:test \
                            bash -c "pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml"
                    """
                }
                // Publish integration test results to show test stage
                junit allowEmptyResults: true, testResults: "${REPORTS_DIR}/integration.xml"
            }
        }

        stage('Deploy to Production') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "Deploying to production..."
                    sh """
                        docker compose -f ${PROD_COMPOSE} down || true
                        docker compose -f ${PROD_COMPOSE} up -d --build
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Archiving all test reports..."
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
        }
        failure {
            echo " Pipeline failed! Check the logs above."
        }
        success {
            echo " Pipeline completed successfully!"
        }
    }
}
