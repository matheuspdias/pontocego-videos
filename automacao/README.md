# Publicação automática do Ponto Cego

Toda **segunda e quarta à noite** uma tarefa agendada do Claude faz o vídeo de terça e de quinta (passo a passo em `AUTOMATICO.md`)
e coloca na fila (`fila/<slug>.json`). O GitHub Actions renderiza e envia ao YouTube **agendado para as 18h** do dia seguinte.

Janela de veto: o vídeo aparece no YouTube Studio como **Programado** desde a noite anterior. Para barrar, edite, deixe privado ou exclua por lá.

## Configuração (uma vez, ~15 min)

### 1. Projeto no Google Cloud
1. Entre em https://console.cloud.google.com com a conta Google **dona do canal Ponto Cego** e crie um projeto (ex.: `ponto-cego-publicador`).
2. **APIs e serviços > Biblioteca**: procure **YouTube Data API v3** e clique em **Ativar**.
3. **Google Auth Platform** (ou "Tela de consentimento OAuth"): clique em começar.
   - Tipo de usuário: **Externo**. Nome do app: `Ponto Cego Publicador`. E-mails: o seu.
   - Em **Público**, clique em **Publicar app** para passar de "Teste" para **Em produção**.
     Isso é importante: em modo Teste o Google invalida o acesso a cada 7 dias e a automação para.
     Não precisa enviar para verificação; é um app só seu.
4. **Clientes > Criar cliente**: tipo **App para computador**. Baixe o JSON (`client_secret_....json`).

### 2. Gerar o token (no seu computador)
```bash
git clone https://github.com/matheuspdias/pontocego-videos && cd pontocego-videos
pip install google-auth-oauthlib
python automacao/autorizar_youtube.py ~/Downloads/client_secret_XXXX.json
```
- O navegador abre. Entre na conta do canal e, se aparecer a lista de canais, escolha **Ponto Cego**.
- Vai aparecer "O Google não verificou este app": clique em **Avançado > Acessar Ponto Cego Publicador (não seguro)**. É o seu próprio app.
- O script imprime 3 valores. **Não compartilhe** esses valores nem faça commit do JSON.

### 3. Secrets no GitHub
Em https://github.com/matheuspdias/pontocego-videos/settings/secrets/actions, crie 3 **repository secrets**:
`YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

### 4. Thumbnail personalizada
O YouTube só aceita thumbnail enviada por API se o canal estiver verificado por telefone: https://www.youtube.com/verify

## No dia a dia
- **Ver o que vai sair:** YouTube Studio > Conteúdo (status Programado), ou a pasta `fila/publicados/` neste repo.
- **Acompanhar o render:** aba **Actions** do repositório. Se falhar, o GitHub manda e-mail. O MP4 fica 7 dias como artefato da execução.
- **Sugerir temas:** escreva na seção "Ideias" de `temas.md`.
- **Pausar a automação:** pause as tarefas agendadas no Claude. Para só barrar um vídeo que já está na fila e ainda não rodou, apague o `fila/<slug>.json`.
- **Rodar à mão:** Actions > Publicar no YouTube > Run workflow (com "sem_upload" marcado ele só renderiza).

## Arquivos
- `publicar.py`: baixa os áudios, junta, renderiza e envia (usado pelo workflow).
- `autorizar_youtube.py`: gera o token, roda uma vez no seu PC.
- `AUTOMATICO.md`: instruções da tarefa agendada.
- `temas.md`: histórias já feitas e ideias.
- `../.github/workflows/publicar.yml`: o workflow.
