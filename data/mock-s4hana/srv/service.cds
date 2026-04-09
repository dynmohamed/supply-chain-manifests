using sap.supplychain from '../db/schema';

service SupplyChainService {
    entity Vendors as projection on supplychain.Vendors;
    entity Materials as projection on supplychain.Materials;
    entity PurchaseRequisitions as projection on supplychain.PurchaseRequisitions;
}
// UI Annotations for the Dashboard
annotate SupplyChainService.PurchaseRequisitions with @(
    UI: {
        LineItem: [
            { Value: ID, Label: 'PR Number' },
            { 
                Value: riskProbability, 
                Label: 'Risk Probability (%)',
                Criticality: #Medium // Hna kiy-jiw l-alwan
            },
            { Value: vendor_ID, Label: 'Vendor' },
            { Value: material_ID, Label: 'Material' },
            { Value: LineItemValue, Label: 'Total Value ($)' },
            { Value: ShipmentMode, Label: 'Mode' },
            { Value: riskMitigation, Label: 'AI Recommendation' }
        ],
        // ... (HeaderInfo dyalk)
    }
);