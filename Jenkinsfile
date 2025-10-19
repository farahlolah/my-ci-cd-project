pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "farah16629/myapp"
        DOCKER_NETWORK = "my-ci-cd-pipeline-net"
        REPORTS_DIR = "reports"
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📦 Checking out source code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_IMAGE}:latest .
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    mkdir -p ${REPORTS_DIR}
                    docker run --rm --network ${DOCKER_NETWORK} \
                        -v $PWD/${REPORTS_DIR}:/app/reports \
                        ${DOCKER_IMAGE}:latest bash -c "
                            PYTHONPATH=/app pytest /app/tests/unit -q --junitxml=/app/reports/unit.xml
                        "
                '''
            }
        }

        stage('Run Integration Tests') {
            steps {
                echo '🧩 Running integration tests...'
                sh '''
                    docker run --rm --network ${DOCKER_NETWORK} \
                        -v $PWD/${REPORTS_DIR}:/app/reports \
                        ${DOCKER_IMAGE}:latest bash -c "
                            PYTHONPATH=/app pytest /app/tests/integration -q --junitxml=/app/reports/integration.xml
                        "
                '''
            }
        }

        stage('Deploy to Production') {
            steps {
                echo '🚢 Deploying to production environment...'
                sh '''
                    docker compose -f docker-compose.prod.yml down
                    docker compose -f docker-compose.prod.yml up -d --build
                '''
            }
        }

        stage('Post Actions') {
            steps {
                script {
                    echo '📊 Collecting and publishing test results...'

                    if (fileExists("${REPORTS_DIR}/unit.xml") || fileExists("${REPORTS_DIR}/integration.xml")) {
                        junit allowEmptyResults: true, testResults: "${REPORTS_DIR}/*.xml"
                    } else {
                        echo '⚠️ No test results found, skipping junit step.'
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build and deployment completed successfully!'
        }
        unstable {
            echo '⚠️ Build completed but with unstable results (e.g., test warnings).'
        }
        failure {
            echo '❌ Build failed. Please check the Jenkins logs.'
        }
    }
}
