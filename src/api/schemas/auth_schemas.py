from ninja import Schema


class TokenRequestSchemaIn(Schema):
    """Credentials used to request an authentication token."""

    username: str
    password: str


class TokenRequestSchemaOut(Schema):
    """Authentication token response."""

    access_token: str
    refresh_token: str
    expires_in: int


class RefreshTokenRequestSchemaIn(Schema):
    """Schema for refresh token request"""
    refresh_token: str
