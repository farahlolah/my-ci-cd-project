pipeline {
    agent any

    environment {
        APP_NAME = "my-ci-cd-pipeline_app_1"
        APP_PORT = "8080"
        REPORT_FILE = "report.xml"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📦 Checking out source code..."
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "🏗️ Building Docker images..."
                sh 'docker compose -f docker-compose.yml build'
            }
        }

        stage('Run App') {
            steps {
                echo "🚀 Starting application containers..."
                sh 'docker compose -f docker-compose.yml up -d'
            }
        }

        stage('Wait for App Readiness') {
            steps {
                script {
                    echo "🔍 Waiting for app to be ready..."
                    def retries = 20
                    for (int i = 1; i <= retries; i++) {
                        def result = sh(script: "curl -s http://${APP_NAME}:${APP_PORT}/metrics || true", returnStdout: true).trim()
                        if (result.contains('http_requests_total')) {
                            echo "✅ App is ready!"
                            break
                        } else {
                            echo "Waiting for app... (${i})"
                            sleep(time: 3, unit: 'SECONDS')
                        }
                        if (i == retries) {
                            error("App did not become ready in time.")
                        }
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                echo "🧪 Running Unit Tests..."
                sh '''
                python3 -m venv venv
                source venv/bin/activate
                pip install --upgrade pip
                pip install pytest requests junit-xml
                pytest --junitxml=${REPORT_FILE} || true
                '''
            }
            post {
                always {
                    junit "${REPORT_FILE}"
                }
            }
        }

        stage('Integration Tests') {
            steps {
                echo "🔬 Running Integration Tests..."
                sh '''
                source venv/bin/activate
                pytest --junitxml=${REPORT_FILE} tests/test_integration.py || true
                '''
            }
            post {
                always {
                    junit "${REPORT_FILE}"
                }
            }
        }

        stage('Deploy to Production') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                echo "🚀 Deploying to production..."
                sh 'docker compose -f docker-compose.yml down && docker compose -f docker-compose.yml up -d'
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up workspace..."
            junit allowEmptyResults: true, testResults: "${REPORT_FILE}"
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed! Check the logs above."
        }
    }
}
