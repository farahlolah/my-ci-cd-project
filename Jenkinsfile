pipeline {
    agent {
        docker {
            image 'python:3.10'
            args '-u root' // ensures permissions for installs and volume mounts
        }
    }

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials' // create this in Jenkins Credentials
        DOCKER_IMAGE = "farah16629/myapp"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code from GitHub..."
                git branch: 'main', url: 'https://github.com/farahlolah/my-ci-cd-project.git'
            }
        }

        stage('Verify Python Environment') {
            steps {
                echo "Verifying Python installation inside Docker agent..."
                sh '''
                    which python || echo "Python not found!"
                    python --version || echo "Python command failed!"
                '''
            }
        }

        stage('Install & Unit Tests') {
            steps {
                echo "Installing dependencies and running unit tests..."
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    PYTHONPATH=. pytest tests/unit -q --junitxml=reports/unit.xml
                '''
            }
        }

        stage('Static Analysis') {
            steps {
                echo "Skipping static analysis for now..."
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    echo "Building and pushing Docker image to DockerHub..."
                    docker.withRegistry('', DOCKERHUB_CREDENTIALS) {
                        def img = docker.build("${env.DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                        img.push()
                        img.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo "Deploying to staging environment..."
                sh '''
                    docker-compose -f docker-compose.staging.yml up -d --build
                    sleep 5
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                echo "Running integration tests..."
                sh 'PYTHONPATH=. pytest tests/integration -q --junitxml=reports/integration.xml'
            }
        }

        stage('Deploy to Production') {
            steps {
                echo "Deploying to production environment..."
                sh 'docker-compose -f docker-compose.prod.yml up -d'
            }
        }
    }

    post {
        always {
            echo "Archiving test reports..."
            junit 'reports/**/*.xml'
        }
        failure {
            mail to: 'farahwael158@gmail.com',
                 subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                 body: "Jenkins build failed. Check details at: ${env.BUILD_URL}"
        }
    }
}
