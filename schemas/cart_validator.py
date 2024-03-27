from pydantic import BaseModel, Field, field_validator
import re

class Cart_validator(BaseModel):
    bookid: int
    cart_item_quantity: int