#!/usr/bin/env python3
"""
Test simple de la fonctionnalité de validation
"""

from sku_generator import Component
from main import BOMProcessor, SKUGenerator
import pandas as pd

def test_component_extraction():
    """Tester l'extraction des composants"""
    print("🧪 TEST D'EXTRACTION DES COMPOSANTS")
    print("=" * 50)

    # Créer un DataFrame de test
    electrical_data = {
        'Name': [
            'Résistance 100Ω',
            'Condensateur 10µF',
            'Connecteur USB-C',
            '',  # Composant vide à ignorer
            'LED rouge'
        ],
        'Description': [
            'Résistance 1/4W',
            'Condensateur électrolytique',
            'Connecteur USB Type-C',
            'Description sans nom',
            'LED rouge 5mm'
        ],
        'ComponentType': [
            'Résistances',
            'Condensateurs',
            'Connecteurs',
            'Résistances',
            'Diodes'
        ],
        'Manufacturer': ['Vishay', 'Panasonic', 'Amphenol', 'Unknown', 'Kingbright'],
        'Manufacturer PN': ['RN55C1000B', 'ECA-1HM100', '12401832E4#2A', '', 'L-53HD'],
        'Quantity': [10, 5, 1, 1, 3],
        'Designator': ['R1,R2,R3', 'C1,C2', 'J1', 'R4', 'D1,D2,D3']
    }

    df_electrical = pd.DataFrame(electrical_data)

    # Tester l'extraction
    generator = SKUGenerator()
    processor = BOMProcessor(generator)

    print(f"📊 DataFrame de test: {len(df_electrical)} entrées")

    # Extraire les composants
    components = processor.extract_electrical_components(df_electrical)

    print(f"✅ Composants valides extraits: {len(components)}")
    print(f"❌ Composants ignorés: {len(df_electrical) - len(components)}")

    print(f"\\n📋 COMPOSANTS EXTRAITS:")
    for i, comp in enumerate(components, 1):
        print(f"  {i}. {comp.name} - {comp.component_type}")

    # Tester la génération de SKU pour composants sélectionnés
    print(f"\\n⚙️ TEST DE GÉNÉRATION SKU POUR COMPOSANTS SÉLECTIONNÉS")

    # Sélectionner seulement les 2 premiers composants
    selected_components = {"ELEC": components[:2]}

    print(f"Composants sélectionnés: {len(selected_components['ELEC'])}")
    for comp in selected_components['ELEC']:
        print(f"  - {comp.name}")

    # Générer les SKU
    results = processor.generate_skus_for_selected_components(selected_components)

    print(f"\\n✅ RÉSULTATS:")
    for domain, df in results.items():
        print(f"{domain}: {len(df)} SKU générés")
        for _, row in df.iterrows():
            print(f"  {row['SKU']}: {row['Name']}")

    print(f"\\n🎯 TEST TERMINÉ AVEC SUCCÈS!")

if __name__ == "__main__":
    test_component_extraction()
