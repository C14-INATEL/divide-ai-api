pipeline {

    agent any

    environment {
        RENDER_API_KEY    = credentials('RENDER_API_KEY')
        RENDER_SERVICE_ID = credentials('RENDER_SERVICE_ID')
        DATABASE_URL      = credentials('DATABASE_URL')
    }

    triggers {
        pollSCM('* * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("api-backend:${env.BUILD_ID}", "--target dev .")
                    sh 'mkdir -p artifacts && docker save api-backend:${BUILD_ID} > artifacts/api-backend-${BUILD_ID}.tar'
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'artifacts/api-backend-*.tar', allowEmptyArchive: true
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
                    archiveArtifacts artifacts: 'reports/test-results.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Database Migrations') {
            when {
                expression {
                    env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'origin/main'
                }
            }
            steps {
                script {
                    docker.image("api-backend:${env.BUILD_ID}").inside("-e DATABASE_URL=${env.DATABASE_URL}") {
                        sh '''
                            echo "Running database migrations..."
                            python -m alembic upgrade head
                            echo "Migrations completed successfully!"
                        '''
                    }
                }
            }
        }

        stage('Deploy to Render') {
            when {
                expression {
                    env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'origin/main'
                }
            }
            steps {
                script {
                    sh '''
                        echo "Deploying to Render..."

                        RESPONSE=$(curl -s -w "\n%{http_code}" \
                            -X POST "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \
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
            deleteDir()
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