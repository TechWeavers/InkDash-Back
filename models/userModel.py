from pydantic import BaseModel
class User(BaseModel): 
    # o id do usuario é gerado pelo próprio mongo
    username: str
    email:str | None = None
    password:str
  


