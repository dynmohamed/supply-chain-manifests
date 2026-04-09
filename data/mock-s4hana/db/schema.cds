namespace sap.supplychain;

entity Vendors {
    key ID : String;
    Name   : String;
    Country: String;
}

entity Materials {
    key ID         : String;
    Description    : String;
    UnitWeight_kg  : Decimal(10,2);
}

entity PurchaseRequisitions {
    key ID           : String;
    vendor           : Association to Vendors;
    material         : Association to Materials;
    Quantity         : Integer;
    LineItemValue    : Decimal(15,2);
    FreightCost_USD  : Decimal(15,2);
    DeliveryQuarter  : Integer;
    ShipmentMode     : String;
    ProcessingTime   : Integer;
}