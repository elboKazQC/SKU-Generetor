#!/usr/bin/env python3
"""
Module d'intégration ODOO pour le générateur de SKU
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
from odoo_export_config import ODOOExportConfig, prepare_odoo_export

class ODOOIntegration:
    """Gestionnaire d'intégration avec ODOO"""

    def __init__(self):
        self.config = ODOOExportConfig()

    def export_to_odoo_csv(self, results: dict, output_file: str = "odoo_import.csv"):
        """Exporter les résultats vers un CSV compatible ODOO"""

        all_products = []

        # Combiner tous les domaines
        for domain, df in results.items():
            if not df.empty:
                # Préparer les données pour ODOO
                odoo_products = prepare_odoo_export(df)
                all_products.extend(odoo_products)

        if all_products:
            # Créer le DataFrame ODOO
            odoo_df = pd.DataFrame(all_products)

            # Exporter vers CSV avec séparateur ODOO
            odoo_df.to_csv(output_file, index=False, sep=';', encoding='utf-8')

            return len(all_products), output_file

        return 0, None

    def export_to_odoo_json(self, results: dict, output_file: str = "odoo_import.json"):
        """Exporter vers JSON pour API ODOO"""

        all_products = []

        for domain, df in results.items():
            if not df.empty:
                odoo_products = prepare_odoo_export(df)
                all_products.extend(odoo_products)

        if all_products:
            # Structure pour API ODOO
            odoo_data = {
                'model': 'product.product',
                'method': 'create',
                'data': all_products,
                'context': {
                    'lang': 'fr_FR',
                    'tz': 'America/Toronto'
                }
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(odoo_data, f, indent=2, ensure_ascii=False)

            return len(all_products), output_file

        return 0, None

    def create_import_template(self, output_file: str = "template_import_odoo.xlsx"):
        """Créer un template Excel pour import ODOO"""

        # Colonnes obligatoires ODOO
        columns = [
            'default_code',      # SKU
            'name',              # Nom
            'description',       # Description
            'categ_id',          # Catégorie
            'type',              # Type produit
            'uom_id',            # Unité
            'standard_price',    # Prix coût
            'list_price',        # Prix vente
            'manufacturer_name', # Fabricant
            'manufacturer_pname',# Réf. fabricant
            'active',            # Actif
            'sale_ok',           # Vendable
            'purchase_ok'        # Achetable
        ]

        # Exemple de données
        example_data = [
            {
                'default_code': 'ELEC-ELEC-STD-RESIST-AAAA',
                'name': 'Résistance 100Ω',
                'description': 'Résistance carbone 100Ω 1/4W',
                'categ_id': 'Composants Électroniques',
                'type': 'product',
                'uom_id': 'Unité(s)',
                'standard_price': 0.05,
                'list_price': 0.10,
                'manufacturer_name': 'Vishay',
                'manufacturer_pname': 'CFR25J100R',
                'active': True,
                'sale_ok': True,
                'purchase_ok': True
            },
            {
                'default_code': 'MECA-MECA-STD-VIS-AAAA',
                'name': 'Vis CHC M6x20',
                'description': 'Vis à tête cylindrique hexagonale M6x20',
                'categ_id': 'Composants Mécaniques',
                'type': 'product',
                'uom_id': 'Unité(s)',
                'standard_price': 0.25,
                'list_price': 0.50,
                'manufacturer_name': 'Unbrako',
                'manufacturer_pname': 'CHC_M6_20',
                'active': True,
                'sale_ok': True,
                'purchase_ok': True
            }
        ]

        # Créer le DataFrame
        template_df = pd.DataFrame(example_data)

        # Exporter vers Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Feuille avec exemples
            template_df.to_excel(writer, sheet_name='Exemples', index=False)

            # Feuille vide pour import
            empty_df = pd.DataFrame(columns=columns)
            empty_df.to_excel(writer, sheet_name='Import_ODOO', index=False)

            # Feuille documentation
            doc_data = {
                'Colonne': columns,
                'Description': [
                    'Code article unique (SKU)',
                    'Nom du produit',
                    'Description détaillée',
                    'Catégorie produit',
                    'Type: product, consu, service',
                    'Unité de mesure',
                    'Prix de revient',
                    'Prix de vente',
                    'Nom du fabricant',
                    'Référence fabricant',
                    'Produit actif (True/False)',
                    'Peut être vendu (True/False)',
                    'Peut être acheté (True/False)'
                ],
                'Obligatoire': [
                    'Oui', 'Oui', 'Non', 'Oui', 'Oui', 'Oui',
                    'Non', 'Non', 'Non', 'Non', 'Oui', 'Non', 'Non'
                ]
            }
            doc_df = pd.DataFrame(doc_data)
            doc_df.to_excel(writer, sheet_name='Documentation', index=False)

        return output_file

    def validate_odoo_data(self, df: pd.DataFrame) -> List[str]:
        """Valider les données pour ODOO"""

        errors = []

        # Vérifier les colonnes obligatoires
        required_cols = ['default_code', 'name', 'categ_id', 'type', 'uom_id']

        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Colonne obligatoire manquante: {col}")
            elif df[col].isnull().any():
                errors.append(f"Valeurs vides dans la colonne obligatoire: {col}")

        # Vérifier l'unicité des SKU
        if 'default_code' in df.columns:
            duplicates = df['default_code'].duplicated()
            if duplicates.any():
                dup_skus = df[duplicates]['default_code'].tolist()
                errors.append(f"SKU dupliqués: {dup_skus}")

        # Vérifier le format des SKU
        if 'default_code' in df.columns:
            invalid_skus = []
            for sku in df['default_code']:
                if not isinstance(sku, str) or len(sku.split('-')) != 5:
                    invalid_skus.append(sku)

            if invalid_skus:
                errors.append(f"Format SKU invalide: {invalid_skus}")

        return errors

def demo_odoo_integration():
    """Démonstration de l'intégration ODOO"""

    print("🔧 DÉMONSTRATION INTÉGRATION ODOO")
    print("=" * 50)

    # Créer l'intégrateur
    odoo = ODOOIntegration()

    # Créer le template
    template_file = odoo.create_import_template()
    print(f"✅ Template créé: {template_file}")

    # Données d'exemple
    example_results = {
        'Électrique': pd.DataFrame([
            {
                'SKU': 'ELEC-ELEC-STD-RESIST-AAAA',
                'Name': 'Résistance 100Ω',
                'Description': 'Résistance carbone 100Ω 1/4W',
                'Domain': 'ÉLECTRIQUE',
                'ComponentType': 'RESIST',
                'Manufacturer': 'Vishay',
                'Manufacturer_PN': 'CFR25J100R',
                'Quantity': 10
            }
        ]),
        'Mécanique': pd.DataFrame([
            {
                'SKU': 'MECA-MECA-STD-VIS-AAAA',
                'Name': 'Vis CHC M6x20',
                'Description': 'Vis hexagonale M6x20',
                'Domain': 'MÉCANIQUE',
                'ComponentType': 'VIS',
                'Manufacturer': 'Unbrako',
                'Manufacturer_PN': 'CHC_M6_20',
                'Quantity': 20
            }
        ])
    }

    # Export CSV
    count_csv, file_csv = odoo.export_to_odoo_csv(example_results)
    print(f"✅ Export CSV: {count_csv} produits → {file_csv}")

    # Export JSON
    count_json, file_json = odoo.export_to_odoo_json(example_results)
    print(f"✅ Export JSON: {count_json} produits → {file_json}")

    print("\n🎯 FICHIERS PRÊTS POUR ODOO:")
    print(f"📄 Template Excel: {template_file}")
    print(f"📄 Import CSV: {file_csv}")
    print(f"📄 API JSON: {file_json}")

if __name__ == "__main__":
    demo_odoo_integration()
