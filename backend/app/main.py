from fastapi import FastAPI
from app.routers import predict, recipes

app = FastAPI(
    title="Let Them Cook API",
    description="Backend for food recognition and recipe recommendation",
    version="1.0.0"
)

#Include routers
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Let Them Cook API"}