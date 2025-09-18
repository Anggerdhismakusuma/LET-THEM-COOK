from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/")
async def predict_food(file: UploadFile = File(...)):
    # TODO: load model and make prediction
    return {"filename": file.filename, "prediction": "dummy_food"}