from ninja import ModelSchema
from pydantic import field_validator
from core.models import DogUserModel
from ninja import ModelSchema, Schema


class DogUserSchemaOut(ModelSchema):
    """Schema for dog user responses."""

    class Meta:
        model = DogUserModel
        fields = ["id", "username", "favorite_toy"]


class DogUserCreateSchemaIn(ModelSchema):
    """Schema for creating a dog user."""

    username: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username_not_empty(cls, v: str) -> str:
        """Ensure username isn't just whitespace"""
        if not v.strip() or len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    class Meta:
        model = DogUserModel
        fields = ["username"]


class DogUserUpdateSchemaIn(ModelSchema):
    """Schema for updating dog users"""

    username: str | None = None
    favorite_toy: str | None = None

    class Meta:
        model = DogUserModel
        fields = ["username", "favorite_toy"]
        fields_optional = ["username", "favorite_toy"]

class DogUserWithTokenSchemaOut(Schema):
    """Schema for dog user with token response"""
    user: DogUserSchemaOut
    token: str