pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker rmi api-backend:latest || true
                    docker build -t api-backend:latest .
                '''
            }
        }
    }

    post {

        success {
            echo 'Build concluído com sucesso!'
        }

        failure {
            echo 'Build falhou!'
        }
    }
}