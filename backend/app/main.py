from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Purchase, User, Vehicle
from .schemas import (AuthResponse, OrderUpdate, PaymentIntent, PurchaseRead, PurchaseRequest, RegisterResponse, RestockRequest, 
                      UserLogin, UserProfileUpdate, UserRead, UserRegister, VehicleCreate, VehicleList, VehicleRead, VehicleUpdate)
from .security import admin_user, create_token, current_user, hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Apex Motors Inventory API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:5174"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    # Administrators are provisioned only through the trusted bootstrap command.
    user = User(
        name=data.name, 
        email=data.email.lower(), 
        password_hash=hash_password(data.password), 
        role="user",
        phone=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        profile_picture=None,
        email_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": user}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_token(user), "user": user}


@app.get("/api/vehicles", response_model=VehicleList)
def list_vehicles(_: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.query(Vehicle).order_by(Vehicle.created_at.desc()).all()
    return {"items": items, "total": len(items)}


@app.get("/api/vehicles/search", response_model=VehicleList)
def search_vehicles(make: str | None = None, model: str | None = None, category: str | None = None, min_price: float | None = None, max_price: float | None = None, _: User = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(Vehicle)
    if make: query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model: query = query.filter(Vehicle.model.ilike(f"%{model}%"))
    if category: query = query.filter(Vehicle.category.ilike(f"%{category}%"))
    if min_price is not None: query = query.filter(Vehicle.price >= min_price)
    if max_price is not None: query = query.filter(Vehicle.price <= max_price)
    items = query.order_by(Vehicle.created_at.desc()).all()
    return {"items": items, "total": len(items)}


@app.post("/api/vehicles", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(data: VehicleCreate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle); db.commit(); db.refresh(vehicle)
    return vehicle


@app.put("/api/vehicles/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
    for field, value in data.model_dump(exclude_unset=True).items(): setattr(vehicle, field, value)
    db.commit(); db.refresh(vehicle)
    return vehicle


@app.delete("/api/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle); db.commit()


@app.post("/api/vehicles/{vehicle_id}/restock", response_model=VehicleRead)
def restock_vehicle(vehicle_id: int, data: RestockRequest, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle.quantity += data.quantity
    db.commit(); db.refresh(vehicle)
    return vehicle


# User Profile Management
@app.get("/api/user/profile", response_model=UserRead)
def get_user_profile(user: User = Depends(current_user)):
    return user


@app.put("/api/user/profile", response_model=UserRead)
def update_user_profile(data: UserProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for field, value in data.model_dump(exclude_unset=True).items():
        if hasattr(user, field):
            setattr(user, field, value)
    db.commit(); db.refresh(user)
    return user


# Payment Processing (Mock Stripe Integration)
@app.post("/api/payments/create-intent")
def create_payment_intent(data: PaymentIntent, user: User = Depends(current_user)):
    # Mock Stripe payment intent creation
    # In production, this would call stripe.PaymentIntent.create()
    import secrets
    payment_id = f"pi_{secrets.token_hex(24)}"
    return {
        "payment_id": payment_id,
        "amount": data.amount,
        "currency": data.currency,
        "status": "requires_payment_method",
        "client_secret": f"pi_{secrets.token_hex(32)}_secret_{secrets.token_hex(32)}"
    }


@app.post("/api/payments/confirm")
def confirm_payment(payment_id: str, _: User = Depends(current_user)):
    # Mock payment confirmation
    # In production, this would verify with Stripe
    return {"payment_id": payment_id, "status": "succeeded"}


# Enhanced Order Management
@app.get("/api/orders", response_model=list[PurchaseRead])
def get_user_orders(user: User = Depends(current_user), db: Session = Depends(get_db)):
    orders = db.query(Purchase).filter(Purchase.user_id == user.id).order_by(Purchase.purchased_at.desc()).all()
    return orders


@app.get("/api/orders/{order_id}", response_model=PurchaseRead)
def get_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    order = db.get(Purchase, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return order


@app.put("/api/orders/{order_id}", response_model=PurchaseRead)
def update_order(order_id: int, data: OrderUpdate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    order = db.get(Purchase, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if hasattr(order, field):
            setattr(order, field, value)
    db.commit(); db.refresh(order)
    return order


# Enhanced Purchase with Payment
@app.post("/api/vehicles/{vehicle_id}/purchase", response_model=VehicleRead)
def purchase_vehicle(vehicle_id: int, data: PurchaseRequest | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
    quantity = data.quantity if data else 1
    if vehicle.quantity < quantity:
        raise HTTPException(status_code=409, detail="Insufficient stock")
    
    # Calculate total amount
    total_amount = vehicle.price * quantity
    
    # Create purchase record
    purchase = Purchase(
        user_id=user.id,
        vehicle_id=vehicle.id,
        quantity=quantity,
        total_amount=total_amount,
        status="pending",
        payment_method=data.payment_method if data else "stripe",
        payment_status="unpaid",
        shipping_address=(data.shipping_address if data else None) or user.address,
        customer_notes=data.customer_notes if data else None
    )
    
    # Update vehicle stock
    vehicle.quantity -= quantity
    
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    
    return vehicle
