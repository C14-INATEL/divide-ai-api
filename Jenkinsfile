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
                    def img = docker.build("api-backend:${env.BUILD_ID}")
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
        }
        success {
            echo 'Build concluído com sucesso!'
        }

        failure {
            echo 'Build falhou!'
        }
    }
}