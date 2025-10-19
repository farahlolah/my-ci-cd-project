pipeline {
    agent any

    environment {
        STAGING_IMAGE = "farah16629/myapp:staging"
        PROD_IMAGE = "farah16629/myapp:prod"
        NETWORK_NAME = "my-ci-cd-pipeline-net"
        APP_PORT = "8080"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                sh """
                docker build -t ${STAGING_IMAGE} .
                docker build -t ${PROD_IMAGE} .
                """
            }
        }

        stage('Create Docker Network') {
            steps {
                sh """
                if ! docker network ls | grep -w ${NETWORK_NAME}; then
                    docker network create ${NETWORK_NAME}
                fi
                """
            }
        }

        stage('Deploy Staging') {
            steps {
                sh """
                docker rm -f app_staging || true
                docker run -d --name app_staging --network ${NETWORK_NAME} -p 8081:${APP_PORT} ${STAGING_IMAGE}
                """
            }
        }

        stage('Wait for Staging App') {
            steps {
                sh """
                echo "Waiting for staging app..."
                for i in \$(seq 1 20); do
                    curl -s http://app_staging:${APP_PORT}/metrics && break
                    echo "Still waiting..." && sleep 3
                done
                """
            }
        }

        stage('Run Integration Tests on Staging') {
            steps {
                sh """
                docker run --rm --network ${NETWORK_NAME} -v \$(pwd)/tests:/app/tests -v \$(pwd)/reports:/app/reports ${STAGING_IMAGE} \
                bash -c "PYTHONPATH=/app pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml"
                """
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh """
                docker run --rm -v \$(pwd)/tests:/app/tests -v \$(pwd)/reports:/app/reports ${STAGING_IMAGE} \
                bash -c "PYTHONPATH=/app pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml"
                """
            }
        }

        stage('Deploy Production') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh """
                docker rm -f app_prod || true
                docker run -d --name app_prod --network ${NETWORK_NAME} -p 8082:${APP_PORT} ${PROD_IMAGE}
                """
            }
        }
    }

    post {
        always {
            // Publish test reports
            junit 'reports/*.xml'

            // Clean up staging container only (keep prod running)
            sh """
            docker rm -f app_staging || true
            docker network rm ${NETWORK_NAME} || true
            """
        }

        success {
            echo "Pipeline finished successfully!"
        }

        unstable {
            echo "Pipeline finished but some tests failed."
        }

        failure {
            echo "Pipeline failed!"
        }
    }
}
