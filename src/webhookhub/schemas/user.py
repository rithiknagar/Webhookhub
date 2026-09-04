from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponseSchema(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True,
    }