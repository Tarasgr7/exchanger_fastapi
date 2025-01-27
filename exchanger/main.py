from fastapi import FastAPI
from .dependencies import Base, engine
from .routers import auth,categories,expenses,analytics,users


app=FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(analytics.router)
app.include_router(users.router)

