from pydantic import BaseModel


class CarrierVerifyResponse(BaseModel):
    verified: bool
    carrier_name: str | None
    dot_number: int | None
