pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "farah16629/myapp"
        STAGING_COMPOSE = "docker-compose.staging.yml"
        PROD_COMPOSE = "docker-compose.prod.yml"
        NETWORK_NAME = "my-ci-cd-pipeline-net"
        REPORT_DIR = "reports"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    mkdir -p ${REPORT_DIR}
                    . venv/bin/activate
                    pytest tests/unit --junitxml=${REPORT_DIR}/unit.xml --maxfail=1 --disable-warnings -q
                '''
            }
            post {
                always {
                    junit 'reports/unit.xml'
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

                    sh '''
                        mkdir -p ${REPORT_DIR}
                        . venv/bin/activate
                        pytest tests/integration --junitxml=${REPORT_DIR}/integration.xml --maxfail=1 --disable-warnings -q
                    '''
                }
            }
            post {
                always {
                    junit 'reports/integration.xml'
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
            echo " Pipeline failed! Check the logs above."
        }
        success {
            echo " Pipeline completed successfully!"
        }
    }
}
