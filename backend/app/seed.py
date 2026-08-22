"""Idempotent local demo inventory seeding command."""
from .database import Base, SessionLocal, engine
from .models import Vehicle

INVENTORY = [
    {"make": "Porsche", "model": "911 Carrera", "category": "Sports", "price": 126000, "quantity": 2},
    {"make": "Range Rover", "model": "Velar Dynamic", "category": "SUV", "price": 68900, "quantity": 4},
    {"make": "Mercedes-Benz", "model": "S 580 4MATIC", "category": "Luxury", "price": 128400, "quantity": 1},
    {"make": "Tesla", "model": "Model S Plaid", "category": "Electric", "price": 89990, "quantity": 0},
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for item in INVENTORY:
            exists = db.query(Vehicle).filter(Vehicle.make == item["make"], Vehicle.model == item["model"]).first()
            if not exists:
                db.add(Vehicle(**item))
        db.commit()
        print("Demo inventory is ready.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
