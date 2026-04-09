import pandas as pd
from catboost import CatBoostClassifier

class SupplyChainPredictor:
    def __init__(self, model_path):
        # 1. 
        self.model = CatBoostClassifier()
        self.model.load_model(model_path)
        self.threshold = 0.375
        
        self.expected_cols = [
                    'Line Item Value', 'Weight (Kilograms)', 'Freight Cost (USD)', 
                    'Processing Time (Days)', 'Shipment Mode_Truck', 
                    'Country_Congo, DRC', 'Country_CÃ´te d\'Ivoire', 
                    'Country_Mozambique', 'Country_Uganda', 'Country_Zambia',
                    'Delivery Quarter_1', 'Delivery Quarter_2', 
                    'Delivery Quarter_3', 'Delivery Quarter_4', 'Vendor_encoded'
                ]

        # 3.
        self.vendor_counts = {
            'SCMS from RDC': 5404, 'Orgenics, Ltd': 754, 'S. BUYS WHOLESALER': 715, 
            'Aurobindo Pharma Limited': 668, 'Trinity Biotech, Plc': 356, 
            'ABBVIE LOGISTICS (FORMERLY ABBOTT LOGISTICS BV)': 347, 'PHARMACY DIRECT': 326, 
            'MYLAN LABORATORIES LTD (FORMERLY MATRIX LABORATORIES)': 317, 'HETERO LABS LIMITED': 277, 
            'CIPLA LIMITED': 175, 'CHEMBIO DIAGNOSTIC SYSTEMS, INC.': 109, 'Standard Diagnostics, Inc.': 98, 
            'STRIDES ARCOLAB LIMITED': 93, 'SHANGHAI KEHUA BIOENGINEERING CO.,LTD.  (KHB)': 70, 
            'MERCK SHARP & DOHME IDEA GMBH (FORMALLY MERCK SHARP & DOHME B.V.)': 68, 'BRISTOL-MYERS SQUIBB': 67, 
            'Orasure Technologies Inc.': 56, 'EMCURE PHARMACEUTICALS LTD': 41, 'ASPEN PHARMACARE': 41, 
            'JSI R&T INSTITUTE, INC.': 38, 'MICRO LABS LIMITED': 35, 'BIO-RAD LABORATORIES (FRANCE)': 28, 
            'Hoffmann-La Roche ltd Basel': 23, 'Abbott GmbH & Co. KG': 21, 'GLAXOSMITHKLINE EXPORT LIMITED': 20, 
            'LAWRENCE LABORATORIES (SUBSIDIARY OF BRISTOL MYERS SQUIBB)': 18, 'IDA FOUNDATION': 17, 
            'Premier Medical Corporation Ltd.': 12, 'REINBOLD EXPORT IMPORT': 12, 
            'INTERNATIONAL HEALTHCARE DISTRIBUTORS': 10, 'SUN PHARMACEUTICAL INDUSTRIES LTD (RANBAXY LABORATORIES LIMITED)': 9, 
            'JANSSEN SCIENCES IRELAND UC (FORMERLY JANSSEN R&D IRELAND)': 7, 'AMSTELFARMA B.V.': 7, 'IDIS LIMITED': 6, 
            'ZEPHYR BIOMEDICALS': 5, 'NOVARTIS PHARMA SERVICES AG': 5, 'BIOLYTICAL LABORATORIES INC.': 5, 
            'IMRES B.V.': 4, 'GILEAD SCIENCES IRELAND, INC.': 4, 'ABBVIE, SRL (FORMALLY ABBOTT LABORATORIES INTERNATIONAL CO.)': 4, 
            'SWORDS LABORATORIES': 3, 'MISSIONPHARMA A/S': 3, 'TURE PHARMACEUTICALS & MEDICAL SUPPLIES P.L.C.': 3, 
            'ACCOUN NIGERIA LIMITED': 3, 'HUMAN GMBH': 3, 'WAGENIA': 2, 'INVERNESS MEDICAL INNOVATIONS HONG KONG LTD': 2, 
            'ETHNOR DEL ISTMO S.A.': 2, 'B&C GROUP S.A.': 2, 'MSD LATIN AMERICA SERVICES, S. DE R.L. DE C.V.': 2, 
            'RANBAXY Fine Chemicals LTD.': 2, 'BUNDI INTERNATIONAL DIAGNOSTICS LTD': 2, 'EY Laboratories': 2, 
            'INVERNESS MEDICAL INNOVATIONS SOUTH AFRICA (PTY) LTD': 2, 'KAS MEDICS LIMITED': 1, 
            'THE MEDICAL EXPORT GROUP BV': 1, 'ABBOTT LOGISTICS B.V.': 1, 'MEDMIRA EAST AFRICA LTD.': 1, 
            'SYSMEX AMERICA INC': 1, 'ACCESS BIO, INC.': 1, 'RAININ INSTRUMENT, LLC.': 1, 'ACTION MEDEOR E.V.': 1, 
            'ABBOTT LABORATORIES (PUERTO RICO)': 1, 'AHN (PTY) LTD (AKA UCB (S.A.)': 1, 'ACOUNS NIGERIA LTD': 1, 
            'SUB-SAHARAN BIOMEDICAL P.L.C.': 1, 'PUETRO RICO PHARMACEUTICAL, INC.': 1, 'SETEMA LIMITED PLC': 1, 
            'BIO-RAD LABORATORIES PTY LTD. (SOUTH AFRICA)': 1, 'OMEGA DIAGNOSTICS LTD': 1, 'PLURIPHARM S.A.': 1, 
            'CENTRAL PHARMACEUTICAL COMPANY NO. 1': 1, 'AUROBINDO PHARAM (SOUTH AFRICA)': 1
        }

    def preprocess_data(self, raw_data):
        """
        raw_data = JSON li jay men SAP CAP
        """
        # A.
        df = pd.DataFrame(columns=self.expected_cols)
        df.loc[0] = 0 

        # B. Valeurs Numériques Directes
        df['Line Item Value'] = raw_data['LineItemValue']
        df['Weight (Kilograms)'] = raw_data['Weight']
        df['Freight Cost (USD)'] = raw_data['FreightCost_USD']
        df['Processing Time (Days)'] = raw_data['ProcessingTime']

        # C. One-Hot Encoding Manuel (Mapping)
        # Shipment Mode
        if raw_data['ShipmentMode'] == 'Truck':
            df['Shipment Mode_Truck'] = 1
            
        # Country
        country_col = f"Country_{raw_data['Country']}"
        if country_col in self.expected_cols:
            df[country_col] = 1
            
        # Delivery Quarter
        quarter_col = f"Delivery Quarter_{raw_data['DeliveryQuarter']}"
        if quarter_col in self.expected_cols:
            df[quarter_col] = 1

        # D. Vendor Frequency Encoding
        vendor_name = raw_data['Vendor']

        df['Vendor_encoded'] = self.vendor_counts.get(vendor_name, 1) 

        return df[self.expected_cols]

    def predict(self, raw_data):

        processed_df = self.preprocess_data(raw_data)
        
        delay_prob = self.model.predict_proba(processed_df)[0][1]
        is_delayed = int(delay_prob >= self.threshold)
        
        return {
            "delay_probability": float(delay_prob),
            "prediction": is_delayed
        }