# Guia de Deploy no Streamlit Cloud

Este guia descreve como colocar o projeto em produção no Streamlit Cloud e como configurar as credenciais de forma segura.

## 1. Preparação (Já realizada)

O projeto já está configurado com:
*   `requirements.txt`: Lista de dependências atualizada.
*   `.gitignore`: Garante que `credentials.json` e arquivos sensíveis não sejam enviados ao GitHub.
*   `app.py`: Lógica para ler credenciais tanto localmente (`credentials.json`) quanto na nuvem (`st.secrets`).

## 2. GitHub

1.  Crie um novo repositório no GitHub.
2.  Envie os arquivos do projeto para lá:
    ```bash
    git init
    git add .
    git commit -m "Deploy inicial"
    git branch -M main
    git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
    git push -u origin main
    ```

## 3. Streamlit Cloud

1.  Acesse [share.streamlit.io](https://share.streamlit.io/).
2.  Clique em **New app**.
3.  Selecione o repositório, branch (`main`) e o arquivo principal (`app.py`).

## 4. Configurando Segredos (Secrets)

**IMPORTANTE:** Esta é a etapa que protege suas credenciais.

1.  Na tela de criação do app (ou nas configurações do app já criado), vá em **Advanced Settings** -> **Secrets**.
2.  Você deve colar o conteúdo do seu arquivo `credentials.json` no formato TOML.
3.  Use o seguinte formato (copie os valores do seu JSON local):

```toml
[gcp_service_account]
type = "service_account"
project_id = "seu-project-id"
private_key_id = "sua-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n(SUA CHAVE AQUI)\n-----END PRIVATE KEY-----\n"
client_email = "seu-email@..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

*Dica: Copie o valor exato da chave privada do seu arquivo JSON, incluindo os `\n`.*

5.  Clique em **Save** e depois em **Deploy**.

## 5. Soluções de Problemas

*   **ModuleNotFoundError**: Verifique se todas as bibliotecas estão no `requirements.txt`.
*   **Erro de Autenticação**: Verifique se copiou corretamente a chave privada nos Secrets.
