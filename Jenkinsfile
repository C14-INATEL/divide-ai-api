pipeline {

    agent any

    triggers {
        pollSCM('* * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("api-backend:${env.BUILD_ID}", "--target dev .")
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    docker.image("api-backend:${env.BUILD_ID}").inside {
                        sh 'python -m pytest tests/ -v --tb=short'
                    }
                }
            }
        }

    }

    post {
        always {
            cleanWs()
            sh "docker rmi api-backend:${env.BUILD_ID} || true"
        }
        success {
            echo 'Build concluído com sucesso!'
        }
        failure {
            echo 'Build falhou!'
        }
    }
}