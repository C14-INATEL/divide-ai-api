pipeline {

    agent any

    environment {
        RENDER_API_KEY    = credentials('RENDER_API_KEY')
        RENDER_SERVICE_ID = credentials('RENDER_SERVICE_ID')
    }

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
                        sh 'mkdir -p reports'
                        sh 'python -m pytest tests/ --junit-xml=reports/test-results.xml --cov-report=xml:reports/coverage.xml'
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
                    archiveArtifacts artifacts: 'reports/coverage.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy to Render') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh '''
                        echo "Deploying to Render..."

                        RESPONSE=$(curl -s -w "\n%{http_code}" \
                            -X POST "https://api.render.com/deploy/${RENDER_SERVICE_ID}" \
                            -H "accept: application/json" \
                            -H "authorization: Bearer ${RENDER_API_KEY}")

                        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
                        BODY=$(echo "$RESPONSE" | head -n1)

                        echo "Status: $HTTP_CODE"
                        echo "Response: $BODY"

                        if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "201" ]; then
                            echo "Deploy falhou! HTTP $HTTP_CODE"
                            exit 1
                        fi

                        echo "Deploy iniciado com sucesso!"
                    '''
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