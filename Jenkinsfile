pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "farah16629/myapp"
        STAGING_COMPOSE = "docker-compose.staging.yml"
        PROD_COMPOSE = "docker-compose.prod.yml"
        DOCKER_NETWORK = "my-ci-cd-pipeline-net"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh """
                    docker build -t $DOCKER_IMAGE:test -f Dockerfile .
                    docker run --rm -w /app $DOCKER_IMAGE:test bash -c "
                        mkdir -p /app/reports && \
                        pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml
                    "
                """
            }
        }

        stage('Docker Build & Push') {
            steps {
                withDockerRegistry([credentialsId: 'dockerhub-credentials', url: 'https://index.docker.io/v1/']) {
                    sh """
                        docker build -t $DOCKER_IMAGE:latest -f Dockerfile .
                        docker push $DOCKER_IMAGE:latest
                    """
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
                    echo "⏳ Waiting for app:8080/metrics to be ready..."
                    sh """
                        for i in {1..10}; do
                            if docker run --rm --network ${DOCKER_NETWORK} curlimages/curl:8.4.0 -fs http://app:8080/metrics > /dev/null; then
                                echo '✅ App is ready!';
                                break;
                            fi;
                            echo '...still waiting (attempt '$i')';
                            sleep 3;
                        done
                    """

                    echo "🚀 Running integration tests..."
                    sh """
                        docker run --rm \
                            --network ${DOCKER_NETWORK} \
                            -v \$(pwd)/reports:/app/reports \
                            $DOCKER_IMAGE:test bash -c "
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
    }
}
