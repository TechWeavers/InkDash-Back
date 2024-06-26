from http.client import HTTPException
from fastapi import Depends, FastAPI, Header
from pydantic import BaseModel
from starlette.responses import JSONResponse
from routes.loginRoute import validar_token
from services.email import EmailSchema, emailEsqueceuSenha
from Controllers.Controller_user import ControllerUser
from fastapi.middleware.cors import CORSMiddleware
from Controllers.token import Token
from datetime import datetime, timedelta
from typing import Annotated
from models.emailModel import emailClass
from models.senhaModel import SenhaClass
 
app = FastAPI()
tokenClass = Token()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
@app.post("/EsqueceuSenha")
async def esqueceu_senha(email: emailClass) -> str: 
    try:
        #for emailusuario in email.email:
        print(email)
        emailUsuario = email.email
        user = ControllerUser.getSingleUser(emailUsuario)
       
        print(user)
        if not user:
            raise HTTPException(404, f"Usuário não encontrado para o e-mail")
        ACCESS_TOKEN_EXPIRE_MINUTES=10
        access_token_expires = timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
        token = tokenClass.create_access_token({"sub": emailUsuario},access_token_expires)
        await emailEsqueceuSenha(user,token) 
        return token
           
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(500, f"Erro ao enviar o e-mail: {str(e)}")
 
@app.put("/RedefinirSenha")
async def redefinir_senha(senhas: SenhaClass, Authorization: Annotated[Header, Depends(validar_token)]) -> JSONResponse:
    if senhas.senha != senhas.senhaConfirmacao:
        return JSONResponse(content={"message": "As senhas precisam ser iguais para a alteração."}, status_code=400)

    try:
        user_data = {"email": Authorization["sub"], "password": senhas.senha}
        ControllerUser.update_user_senha(user_data)
        return {"message": "Senha redefinida com sucesso"}
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar a senha: {str(e)}")