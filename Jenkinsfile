pipeline {
    agent any 

    stages {
        stage('Checkout do Código') {
            steps {
                // Puxa o código da branch que acionou o gatilho
                checkout scm 
            }
        }

        stage('Build: Setup e Dependências') {
            steps {
                // Cria o ambiente e resolve as dependências do pyproject.toml
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install .  
                '''
            }
        }
    }

    // Feedback visual do resultado
    post { 
        always {
            cleanWs() // Limpa o workspace para a próxima execução não herdar lixo
        }
        success {
            echo 'Build finalizado com sucesso! O ambiente foi montado sem erros.'
        }
        failure {
            echo 'Erro no Build! Verifique se há conflito nas dependências.'
        }
    }
}