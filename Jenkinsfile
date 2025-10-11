pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials'
        DOCKER_IMAGE = "farah16629/myapp"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                git branch: 'main', url: 'https://github.com/farahlolah/my-ci-cd-project.git'
            }
        }

        stage('Install & Unit Tests') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root'
                }
            }
            steps {
                echo "Installing dependencies and running unit tests..."
                sh '''
                    echo "=== Checking directory contents ==="
                    pwd
                    ls -R
                    echo "=== Installing dependencies ==="
                    python3 -m pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    echo "=== Running unit tests ==="
                    mkdir -p reports
                    PYTHONPATH=. pytest tests/unit -q --junitxml=reports/unit.xml
                '''
            }
        }

        stage('Static Analysis') {
            steps {
                echo "Skipping static analysis (placeholder stage)..."
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
                        img.push('staging')
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo "=== Cleaning up old containers and network ==="
                sh '''
                    docker stop prometheus || echo "No prometheus container found"
                    docker rm prometheus || echo "Prometheus container already removed"

                    docker stop my-ci-cd-pipeline_app_1 || echo "No app container found"
                    docker rm my-ci-cd-pipeline_app_1 || echo "App container already removed"

                    docker stop my-ci-cd-pipeline_prometheus_1 || echo "No prometheus container found"
                    docker rm my-ci-cd-pipeline_prometheus_1 || echo "Prometheus container already removed"

                    docker network rm my-ci-cd-pipeline_default || echo "No default network found"
                    docker network rm my-ci-cd-pipeline_my-ci-cd-pipeline_default || echo "No secondary default network found"

                    echo "=== Checking if prometheus.yml exists ==="
                    if [ ! -f ./prometheus.yml ]; then
                        echo "Copying prometheus.yml to workspace..."
                        cp /var/jenkins_home/workspace/my-ci-cd-pipeline/prometheus.yml ./prometheus.yml
                    else
                        echo "prometheus.yml already exists, skipping copy."
                    fi

                    echo "=== Starting new staging environment ==="
                    docker-compose -f docker-compose.staging.yml up -d --build
                    sleep 5
                '''
            }
        }

        stage('Integration Tests') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root'
                }
            }
            //steps {
                //echo "Running integration tests..."
                //sh '''
                    //mkdir -p reports
                    //PYTHONPATH=. pytest tests/integration -q --junitxml=reports/integration.xml
                '''
            //}
        //}

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
                 body: "Build failed. View details here: ${env.BUILD_URL}"
        }
    }
}
