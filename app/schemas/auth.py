from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserInToken(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    roles: List[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInToken

class LoginInput(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    model_config = {
        "json_schema_extra": {
             "example": {
                "email": "admin@globomantics.com",
                "password": "password"
            }
        }
    }