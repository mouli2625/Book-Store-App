from pydantic import field_validator, EmailStr, BaseModel, Field, validator
from typing import Optional
import re

class BookValidator(BaseModel):
    title : str 
    author : str
    price : int
    quantity : int