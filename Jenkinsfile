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

        stage('Build') {
            steps {
                script {
                    docker.build("api-backend:${env.BUILD_ID}")
                }
            }
        }
    }
    
    post { 
        always { 
            cleanWs() 
        }
    }
}