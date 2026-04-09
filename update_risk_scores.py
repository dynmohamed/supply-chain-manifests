import pandas as pd
import requests
import time

# 1. Load the existing Mock Data
csv_path = 'mock-s4hana/db/data/sap.supplychain-PurchaseRequisitions.csv'
df = pd.read_csv(csv_path)

# 2. Add new columns if they don't exist
if 'riskProbability' not in df.columns:
    df['riskProbability'] = 0.0
if 'riskMitigation' not in df.columns:
    df['riskMitigation'] = "No Risk Detected"

print(f"🚀 Starting Batch Inference for {len(df)} records...")

# 3. Loop through each row and call your FastAPI Model
for index, row in df.iterrows():
    # Prepare payload exactly like your FastAPI expects
    payload = {
        "Requisition_ID": str(row['ID']),
        "LineItemValue": float(row['LineItemValue']),
        "Weight": float(row['Quantity'] * 1.5), # Assuming average weight
        "FreightCost_USD": float(row['FreightCost_USD']),
        "ProcessingTime": int(row['ProcessingTime']),
        "ShipmentMode": str(row['ShipmentMode']),
        "Country": "USA", # Mock country for inference
        "DeliveryQuarter": int(row['DeliveryQuarter']),
        "Vendor": "Mock Vendor"
    }

    try:
        # Call your FastAPI (Make sure uvicorn is running!)
        response = requests.post('http://localhost:8000/docs#/', json=payload)
        res_data = response.json()
        
        # Update DataFrame with real results
        df.at[index, 'riskProbability'] = round(res_data['delay_probability'] * 100, 1)
        df.at[index, 'riskMitigation'] = res_data.get('llm_recommendation', 'Safe')
        
        if index % 50 == 0:
            print(f"✅ Processed {index} records...")
            
    except Exception as e:
        print(f"❌ Error at row {index}: {e}")

# 4. Save the updated CSV back to the same path
df.to_csv(csv_path, index=False)
print(f"✨ Successfully updated {csv_path} with real AI predictions!")