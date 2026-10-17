"""
Roda UMA VEZ no seu computador para gerar o refresh token do YouTube.

    pip install google-auth-oauthlib
    python automacao/autorizar_youtube.py caminho/do/client_secret.json

Abre o navegador, você entra na conta Google DONA do canal Ponto Cego e escolhe o canal.
No fim ele imprime os 3 valores para colar nos secrets do GitHub.
Não faça commit do client_secret.json nem do token.
"""
import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

ESCOPOS = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

if len(sys.argv) != 2:
    sys.exit("uso: python automacao/autorizar_youtube.py client_secret.json")

flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], ESCOPOS)
cred = flow.run_local_server(port=0, prompt="consent", access_type="offline")

with open(sys.argv[1], encoding="utf-8") as f:
    info = json.load(f)
info = info.get("installed") or info.get("web")

print("\nCole estes 3 valores em GitHub > Settings > Secrets and variables > Actions > New repository secret:\n")
print("YT_CLIENT_ID      =", info["client_id"])
print("YT_CLIENT_SECRET  =", info["client_secret"])
print("YT_REFRESH_TOKEN  =", cred.refresh_token)
