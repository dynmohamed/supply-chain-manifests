const cds = require('@sap/cds');
const axios = require('axios');

module.exports = cds.service.impl(async function() {
    
    // Bind to database entities
    const { PurchaseRequisitions, Vendors, Materials } = this.entities;

    // Trigger after a new Purchase Requisition is created
    this.after('CREATE', 'PurchaseRequisitions', async (req) => {
        console.log(`\n[SAP CAP] 📦 New Purchase Requisition detected: ${req.ID}`);

        try {
            // 1. Fetch related Vendor and Material data from the database
            const vendorData = await SELECT.one.from(Vendors).where({ ID: req.vendor_ID });
            const materialData = await SELECT.one.from(Materials).where({ ID: req.material_ID });

            if (!vendorData || !materialData) {
                console.log("[SAP CAP] ⚠️ Vendor or Material not found. Skipping AI analysis.");
                return;
            }

            // 2. Calculate Total Weight (Quantity * UnitWeight)
            const totalWeight = req.Quantity * materialData.UnitWeight_kg;

            // 3. Prepare the exact JSON payload expected by the Python FastAPI model
            const inferencePayload = {
                "Requisition_ID": req.ID,
                "LineItemValue": parseFloat(req.LineItemValue),
                "Weight": parseFloat(totalWeight),
                "FreightCost_USD": parseFloat(req.FreightCost_USD),
                "ProcessingTime": req.ProcessingTime,
                "ShipmentMode": req.ShipmentMode,
                "Country": vendorData.Country,
                "DeliveryQuarter": req.DeliveryQuarter,
                "Vendor": vendorData.Name
            };

            console.log("[SAP CAP] 🚀 Sending data to AI Agent (FastAPI)...");

            // 4. Call the FastAPI Orchestration Endpoint (Forcing IPv4 to avoid ECONNREFUSED ::1)
            const pythonApiUrl = 'http://127.0.0.1:8000/orchestrate-shipment';
            const response = await axios.post(pythonApiUrl, inferencePayload);
            const aiResult = response.data;

            // 5. Output the results to the SAP terminal
            if (aiResult.trigger_workflow === true) {
                console.log(`[SAP CAP] 🚨 HIGH RISK ALERT! Probability: ${(aiResult.delay_probability * 100).toFixed(1)}%`);
                console.log(`[SAP CAP] 🤖 AI Mitigation Strategy: ${aiResult.llm_recommendation}`);
            } else {
                console.log(`[SAP CAP] ✅ Low Risk. Probability: ${(aiResult.delay_probability * 100).toFixed(1)}%`);
            }
        // Inside your this.after('CREATE', ...)
            await UPDATE(PurchaseRequisitions).set({
                riskProbability: (aiResult.delay_probability * 100).toFixed(1),
                riskMitigation: aiResult.llm_recommendation
            }).where({ ID: req.ID });

        } catch (error) {
            console.error("[SAP CAP] ❌ Error connecting to AI Agent:", error.message);
        }
    });
});