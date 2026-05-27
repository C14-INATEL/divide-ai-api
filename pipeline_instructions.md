# Jenkins + Docker (Setup Local)

## 1. Clonar o projeto

```bash
git clone https://github.com/C14-INATEL/divide-ai-api.git
cd divide-ai-api
```

---

## 2. Subir Jenkins

```bash
docker compose -f docker-compose.jenkins.yml up -d --build
```

---

## 3. Abrir Jenkins

Acessar:

```txt
http://localhost:8080
```

---

## 4. Pegar senha inicial

Ver containers:

```bash
docker ps
```

Ver logs do Jenkins:

```bash
docker logs NOME_DO_CONTAINER
```

Copiar a senha exibida no log.

---

## 5. Configurar Jenkins

- Install Suggested Plugins
- Criar usuário admin

---

## 6. Criar pipeline

- New Item
- Pipeline
- Pipeline script from SCM
- Git

URL:

```txt
https://github.com/C14-INATEL/divide-ai-api.git
```

Branch:

```txt
*/develop
```

Salvar.

---

## 7. Rodar pipeline

```txt
Build Now
```

O Jenkins irá:

- clonar o projeto
- executar o Jenkinsfile
- buildar o container Docker

---

## Comandos úteis

### Parar Jenkins

```bash
docker compose -f docker-compose.jenkins.yml down
```

### Rebuildar Jenkins

Usar apenas se mudar:

- plugins.txt
- jenkins/Dockerfile
- docker-compose.jenkins.yml

```bash
docker compose -f docker-compose.jenkins.yml up -d --build
```

---

## Fluxo normal

Após configurado:

```bash
git push
```

Depois executar novamente:

```txt
Build Now
```

---

## Futuras melhorias

- Webhook GitHub
- Deploy automático
- Jenkins hospedado em servidor
- DockerHub
- Testes automatizados