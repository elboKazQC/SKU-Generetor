#!/usr/bin/env python3
"""
Test avec un BOM simulé contenant des entrées vides
"""

import pandas as pd
from main import BOMProcessor
from sku_generator import SKUGenerator
import logging

# Configuration du logging pour voir les messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_bom_with_empty_entries():
    """Test avec des entrées vides dans un BOM simulé"""
    print("🧪 TEST BOM AVEC ENTRÉES VIDES")
    print("=" * 50)

    # Créer un DataFrame simulé avec des entrées problématiques
    electrical_data = {
        'Name': [
            'Résistance 100Ω',  # Valide
            '',                  # Nom vide
            'nan',              # Nom invalide
            'Condensateur 10µF', # Valide
            '   ',              # Espaces uniquement
            'Diode LED',        # Valide
        ],
        'Description': [
            'Résistance 1/4W',
            'Description sans nom',
            'Description avec nan',
            'Condensateur électrolytique',
            'Description avec espaces',
            'LED rouge 5mm',
        ],
        'ComponentType': [
            'Résistances',
            'Résistances',
            '',  # Type vide
            'Condensateurs',
            'Diodes',
            'Diodes',
        ],
        'Manufacturer': [
            'Vishay',
            'Unknown',
            'Unknown',
            'Panasonic',
            'Unknown',
            'Kingbright',
        ],
        'Manufacturer PN': [
            'RN55C1000B',
            '',
            '',
            'ECA-1HM100',
            '',
            'L-53HD',
        ],
        'Quantity': [1, 1, 1, 2, 1, 5],
        'Designator': ['R1', 'R2', 'R3', 'C1', 'D1', 'D2']
    }

    df_electrical = pd.DataFrame(electrical_data)

    # Créer le processeur
    generator = SKUGenerator()
    processor = BOMProcessor(generator)

    print(f"\n📊 BOM électrique simulé ({len(df_electrical)} entrées):")
    for line_num, (idx, row) in enumerate(df_electrical.iterrows(), start=2):
        status = "❌" if not row['Name'].strip() or row['Name'] == 'nan' or not row['ComponentType'].strip() else "✅"
        print(f"  {status} Ligne {line_num}: '{row['Name']}' - {row['ComponentType']}")

    print(f"\n⚙️ Traitement du BOM électrique...")
    result_df = processor.process_electrical_bom(df_electrical)

    print(f"\n📈 Résultats:")
    print(f"  - Entrées originales: {len(df_electrical)}")
    print(f"  - SKU générés: {len(result_df)}")
    print(f"  - Entrées ignorées: {len(df_electrical) - len(result_df)}")

    if len(result_df) > 0:
        print(f"\n✅ SKU générés avec succès:")
        for _, row in result_df.iterrows():
            print(f"  - {row['SKU']}: {row['Name']}")

    print("\n" + "=" * 50)
    print("🎯 RÉSULTAT: Les entrées vides ont été correctement filtrées!")

if __name__ == "__main__":
    test_bom_with_empty_entries()
