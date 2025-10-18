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
                        docker run --rm -w /app -v \$PWD/reports:/app/reports $DOCKER_IMAGE:test bash -c "pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml"
                    """
                }
                //  Collect results for this stage only
                junit allowEmptyResults: true, testResults: 'reports/unit.xml'
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
                    echo "Waiting for app to be ready..."
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
                        sh "docker logs \$(docker ps -qf name=my-ci-cd-pipeline_app_1 || true)"
                        error("App did not become ready in time.")
                    }

                    sh """
                        docker run --rm --network ${NETWORK_NAME} -v \$PWD/reports:/app/reports $DOCKER_IMAGE:test bash -c "PYTHONPATH=/app pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml"
                    """
                }
                // Collect results for this stage only
                junit allowEmptyResults: true, testResults: 'reports/integration.xml'
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
        failure {
            echo "Pipeline failed! Check the logs above."
        }
        success {
            echo "Pipeline completed successfully!"
        }
    }
}
