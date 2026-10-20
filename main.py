from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import traceback

DATABASE_URL = "sqlite:///./ticket.db"

engine = create_engine(DATABASE_URL,
                       connect_args = {"check_same_thread": False}
                       
                       )
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
Base = declarative_base()


class TicketDB(Base):
    __tablename__ = "tickets"

    id = Column(Integer,
                primary_key =True, index=True
                )
    message = Column(String)
    category = Column(String)

Base.metadata.create_all(bind=engine)


app =FastAPI()

import logging
logging.basicConfig(level=logging.DEBUG)


model = joblib.load('support_ticket_classifier.pkl')
le = joblib.load('label_encoder.pkl')

class Ticket(BaseModel):
    message:str

@app.get('/')
def home():
    return {
        "message": "Support Ticket Classifier API is running"
    }

@app.post("/predict")
def predict_ticket(ticket:Ticket):
    try:
        print(f"INPUT: {ticket.message}")
        prediction = model.predict([ticket.message])
        print(f"PREDICTION NUM: {prediction}")

        category = le.inverse_transform(prediction)[0]
        print(f"CATEGORY: {category}")

        db = SessionLocal()
        new_ticket = TicketDB(
        message = ticket.message,
        category = category
     )

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        db.close()

        return{
        "id": new_ticket.id,
        "message": new_ticket.message,
        "category": new_ticket.category
     }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/tickets')
def get_tickets():

    db = SessionLocal()

    tickets = db.query(TicketDB).all()
    db.close()

    return tickets