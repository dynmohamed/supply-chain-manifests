from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from src.model_predictor import SupplyChainPredictor
from src.genai_hub_client import draft_and_send_email

# Initialize the FastAPI application
app = FastAPI(title="Supply Chain Risk Agent API")

# Initialize the ML Predictor (CatBoost)
predictor = SupplyChainPredictor(model_path="models/catboost_scms.cbm")

# Define the expected JSON payload structure from SAP CAP
class ShipmentData(BaseModel):
    Requisition_ID: str
    LineItemValue: float
    Weight: float
    FreightCost_USD: float
    ProcessingTime: int
    ShipmentMode: str
    Country: str
    DeliveryQuarter: int
    Vendor: str

@app.post("/v1/models/supply-chain-risk-agent:predict")
def orchestrate_shipment(data: ShipmentData, background_tasks: BackgroundTasks):
    """
    Receives data from SAP CAP, predicts risk, and triggers an email alert if high risk.
    """
    raw_data = data.dict()
    
    # Step 1: Get Prediction from CatBoost Model
    prediction_result = predictor.predict(raw_data)
    delay_probability = prediction_result["delay_probability"]
    
    # Step 2: Prepare default response payload
    response_payload = {
        "requisition_id": raw_data["Requisition_ID"],
        "delay_probability": delay_probability,
        "email_alert_triggered": False
    }

    # Step 3: Evaluate against the strict business threshold (0.375)
    if delay_probability >= predictor.threshold:
        response_payload["email_alert_triggered"] = True
        
        # Execute the email generation and sending in the background
        # This prevents the API from blocking while waiting for the LLM and SMTP
        background_tasks.add_task(draft_and_send_email, raw_data, delay_probability)

    return response_payload
@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "alive", "model_loaded": predictor is not None}