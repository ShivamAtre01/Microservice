pipeline {
    agent { label 'dev' }

    environment {
       DOCKERHUB_USER = 'top017'
    }

    stages {
        stage('Clean Workspace') {
        steps {
            cleanWs()
            }
        }
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
                    docker tag microservice-user-service:latest ${DOCKERHUB_USER}/user-service:latest
                    docker tag microservice-payment-service:latest ${DOCKERHUB_USER}/payment-service:latest
                    docker tag microservice-notification-service:latest ${DOCKERHUB_USER}/notification-service:latest
                    docker tag microservice-order-service:latest ${DOCKERHUB_USER}/order-service:latest
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                    trivy image --severity HIGH,CRITICAL --exit-code 1 ${DOCKERHUB_USER}/user-service:latest
                    trivy image --severity HIGH,CRITICAL --exit-code 1 ${DOCKERHUB_USER}/payment-service:latest
                    trivy image --severity HIGH,CRITICAL --exit-code 1 ${DOCKERHUB_USER}/notification-service:latest
                    trivy image --severity HIGH,CRITICAL --exit-code 1 ${DOCKERHUB_USER}/order-service:latest
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

                        docker push ${DOCKERHUB_USER}/user-service:latest
                        docker push ${DOCKERHUB_USER}/payment-service:latest
                        docker push ${DOCKERHUB_USER}/notification-service:latest
                        docker push ${DOCKERHUB_USER}/order-service:latest

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
