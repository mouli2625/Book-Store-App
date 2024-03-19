from pydantic import field_validator, EmailStr, BaseModel, Field, validator
from typing import Optional
import re
import os
from dotenv import load_dotenv


class UserValidator(BaseModel):
    username : str = Field(max_length=9,min_length=3)
    password : str
    email : EmailStr
    superkey : str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls,value):
        password_pattern=r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&]).{8,}$'
        if re.match(password_pattern,value):
            return value
        raise ValueError(f'Password must contain a special character and uppercase letter')
    
    @validator('superkey')
    def validate_superkey(cls,value):
        result=os.getenv('superkey')
        if value==result:
            return True
        raise ValueError('Incorrect Superkey')
    
    
