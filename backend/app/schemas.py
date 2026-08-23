from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    zip_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=100)
    profile_picture: str | None = Field(default=None, max_length=500)


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    profile_picture: str | None = None
    email_verified: bool = False
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class RegisterResponse(BaseModel):
    user: UserRead


class VehicleCreate(BaseModel):
    make: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class VehicleUpdate(BaseModel):
    make: str | None = Field(default=None, min_length=1, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=60)
    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)


class VehicleRead(VehicleCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class VehicleList(BaseModel):
    items: list[VehicleRead]
    total: int


class RestockRequest(BaseModel):
    quantity: int = Field(gt=0)


class PurchaseRequest(BaseModel):
    vehicle_id: int | None = None
    quantity: int = Field(default=1, ge=1)
    shipping_address: str | None = Field(default=None)
    customer_notes: str | None = Field(default=None)
    payment_method: str = Field(default="stripe")  # stripe, paypal, bank_transfer


class PaymentIntent(BaseModel):
    amount: float
    currency: str = "usd"
    payment_method: str = Field(default="stripe")


class PurchaseRead(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    quantity: int
    status: str
    total_amount: float
    payment_method: str | None = None
    payment_status: str
    payment_id: str | None = None
    payment_date: datetime | None = None
    shipping_address: str | None = None
    tracking_number: str | None = None
    estimated_delivery: datetime | None = None
    actual_delivery: datetime | None = None
    customer_notes: str | None = None
    admin_notes: str | None = None
    purchased_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(BaseModel):
    status: str | None = Field(default=None)
    tracking_number: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
    actual_delivery: datetime | None = Field(default=None)
    admin_notes: str | None = Field(default=None)
