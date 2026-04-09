import pandas as pd
import random
import os

# 1. Qraya dyal l-dataset l-asli
# T2ked bli s-smiya dyal l-fichier s7i7a o kayn f nfss l-dossier
df = pd.read_csv('data/SCMS_Delivery_History_Dataset.csv', encoding="ISO-8859-1")

# N-khtaro 500 ligne 3achwa2iya
df_sample = df.sample(n=500, random_state=42).reset_index(drop=True)

# 2. Création dyal l-dossier db/data/ ila makansh
os.makedirs('mock-s4hana/db/data', exist_ok=True)

# 3. Génération dyal Vendors (sap.supplychain-Vendors.csv)
vendors = df_sample[['Vendor', 'Country']].dropna().drop_duplicates().reset_index(drop=True)
vendors['ID'] = ['VND-' + str(i).zfill(3) for i in range(1, len(vendors) + 1)]
vendors = vendors[['ID', 'Vendor', 'Country']]
vendors.rename(columns={'Vendor': 'Name'}, inplace=True)
vendors.to_csv('mock-s4hana/db/data/sap.supplychain-Vendors.csv', index=False, sep=';')

# 4. Génération dyal Materials (sap.supplychain-Materials.csv)
# Bima an l-dataset ma fihsh Materials, ghan-creeyiwhom syntétiquement
materials_data = {
    'ID': ['MAT-100', 'MAT-200', 'MAT-300', 'MAT-400'],
    'Description': ['Medical Equipment', 'Industrial Pump', 'Lab Supplies', 'Safety Gear'],
    'UnitWeight_kg': [1.5, 12.0, 0.5, 2.2]
}
materials = pd.DataFrame(materials_data)
materials.to_csv('mock-s4hana/db/data/sap.supplychain-Materials.csv', index=False, sep=';')

# 5. Génération dyal Purchase Requisitions (sap.supplychain-PurchaseRequisitions.csv)
# N-qaddo l-mapping dyal les IDs
vendor_dict = dict(zip(vendors['Name'], vendors['ID']))
material_ids = materials['ID'].tolist()

# N-bniw l-DataFrame we7da b we7da bash n-tfadaw moshkil dyal l-Index
prs = pd.DataFrame()
prs['ID'] = ['PR-CAP-' + str(i).zfill(4) for i in range(1, 501)]
prs['vendor_ID'] = df_sample['Vendor'].map(vendor_dict).values
prs['material_ID'] = [random.choice(material_ids) for _ in range(500)]
prs['Quantity'] = [random.randint(100, 5000) for _ in range(500)]
prs['LineItemValue'] = df_sample['Line Item Value'].values
prs['FreightCost_USD'] = df_sample['Freight Cost (USD)'].values
prs['DeliveryQuarter'] = [random.randint(1, 4) for _ in range(500)]
prs['ShipmentMode'] = df_sample['Shipment Mode'].values
prs['ProcessingTime'] = [random.randint(1, 30) for _ in range(500)]

# N-7eydo les lignes li fihom valeurs naqsin (NaN)
prs = prs.dropna()

prs.to_csv('mock-s4hana/db/data/sap.supplychain-PurchaseRequisitions.csv', index=False, sep=';')

print("✅ Kolshi Nadi! L-fichiers t-saybo f mock-s4hana/db/data/")