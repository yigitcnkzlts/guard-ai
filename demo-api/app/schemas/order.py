from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    customer_id: int
    product_name: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

    @field_validator("product_name")
    @classmethod
    def product_name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("product_name must not be empty")
        return value


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    product_name: str
    amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer("amount")
    def serialize_amount(self, amount: Decimal) -> float:
        return float(amount)


class CancelAllResponse(BaseModel):
    cancelled_count: int
    orders: list[OrderRead]
