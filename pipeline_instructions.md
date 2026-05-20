### Guia de Configuração Local: CI/CD com Jenkins e Docker

Este guia descreve os passos para replicar o ambiente de integração contínua. A infraestrutura baseia-se no `Dockerfile` e no `Jenkinsfile` presentes no repositório.

**1. Iniciar o Servidor Jenkins**
Execute o comando no terminal para iniciar o Jenkins com acesso ao Docker local:
`docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock -u root --name jenkins-api jenkins/jenkins:lts`

**2. Instalar o Docker no Jenkins**
Execute os comandos sequenciais para instalar o cliente Docker dentro do contentor:
`docker exec -it jenkins-api apt-get update`
`docker exec -it jenkins-api apt-get install -y docker.io`

**3. Obter a Palavra-passe Inicial**
Recupere a palavra-passe de administrador:
`docker exec -it jenkins-api cat /var/jenkins_home/secrets/initialAdminPassword`

**4. Configurar a Interface Web**
1. Aceda a http://localhost:8080 e insira a palavra-passe.
2. Instale os plugins sugeridos e crie o utilizador.
3. Navegue até Gerir Jenkins > Plugins > Available plugins.
4. Instale o plugin "Docker Pipeline" e reinicie o Jenkins.

**5. Criar e Configurar o Pipeline**
1. Clique em Nova Tarefa, insira um nome, selecione Pipeline e clique em OK.
2. Em Build Triggers, marque Poll SCM e insira * * * * *
3. Em Pipeline, altere o Definition para Pipeline script from SCM.
4. Selecione Git e insira o URL do repositório.
5. Defina o Branch Specifier como */main e guarde.

**6. Ativar a Automação**
Clique em Construir agora (Build Now) na tarefa criada. Esta primeira execução manual é obrigatória para ler o Jenkinsfile e ativar o rastreio automático de novos commits.