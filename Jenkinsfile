pipeline {
    agent { label 'dev' }

    environment {
        DOCKERHUB_USER = 'top017'
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/ShivamAtre01/Microservice.git'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    echo "Testing microservices..."
                    
                    docker compose config
                '''
            }
        }

        stage('Clean') {
            steps {
                sh '''
                    docker compose down --remove-orphans || true
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    docker compose build --no-cache
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                    trivy image ${DOCKERHUB_USER}/user-service:latest || true
                    trivy image ${DOCKERHUB_USER}/payment-service:latest || true
                    trivy image ${DOCKERHUB_USER}/notification-service:latest || true
                    trivy image ${DOCKERHUB_USER}/order-service:latest || true
                '''
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login \
                            -u "$DOCKER_USER" \
                            --password-stdin

                        docker push ${DOCKER_USER}/user-service:latest
                        docker push ${DOCKER_USER}/payment-service:latest
                        docker push ${DOCKER_USER}/notification-service:latest
                        docker push ${DOCKER_USER}/order-service:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose down
                    docker compose up -d
                '''
            }
        }
    }
}
