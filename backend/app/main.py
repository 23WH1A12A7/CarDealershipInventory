from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Purchase, User, Vehicle
from .schemas import AuthResponse, RegisterResponse, RestockRequest, UserLogin, UserRead, UserRegister, VehicleCreate, VehicleList, VehicleRead, VehicleUpdate
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
    user = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password), role="user")
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


@app.post("/api/vehicles/{vehicle_id}/purchase", response_model=VehicleRead)
def purchase_vehicle(vehicle_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.quantity < 1: raise HTTPException(status_code=409, detail="Vehicle is out of stock")
    vehicle.quantity -= 1
    db.add(Purchase(user_id=user.id, vehicle_id=vehicle.id, quantity=1))
    db.commit(); db.refresh(vehicle)
    return vehicle


@app.post("/api/vehicles/{vehicle_id}/restock", response_model=VehicleRead)
def restock_vehicle(vehicle_id: int, data: RestockRequest, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle.quantity += data.quantity
    db.commit(); db.refresh(vehicle)
    return vehicle
