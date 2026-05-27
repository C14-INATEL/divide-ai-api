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