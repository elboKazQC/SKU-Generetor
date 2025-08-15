#!/usr/bin/env python3
"""
Configuration pour l'export vers ODOO
"""

class ODOOExportConfig:
    """Configuration des colonnes pour export ODOO"""

    # Mapping des colonnes pour ODOO
    ODOO_COLUMNS = {
        # Colonnes obligatoires ODOO
        'default_code': 'SKU',                    # Code article (SKU)
        'name': 'Name',                           # Nom article
        'description': 'Description',             # Description
        'categ_id': 'Domain',                     # Catégorie (ELEC/MECA)
        'standard_price': 'Cost',                 # Prix coût
        'list_price': 'Price',                    # Prix vente
        'uom_id': 'Unit',                         # Unité de mesure
        'type': 'Type',                           # Type produit

        # Colonnes fabricant
        'manufacturer_name': 'Manufacturer',      # Nom fabricant
        'manufacturer_pname': 'Manufacturer_PN',  # Référence fabricant

        # Colonnes techniques
        'route_ids': 'Route',                     # Routes logistiques
        'tracking': 'Tracking',                   # Suivi (lot/série)
        'active': 'Active',                       # Actif

        # Colonnes personnalisées
        'x_domain': 'Domain',                     # Domaine technique
        'x_component_type': 'ComponentType',      # Type composant
        'x_designator': 'Designator',             # Désignateur
        'x_quantity_bom': 'Quantity'              # Quantité BOM
    }

    # Valeurs par défaut pour ODOO
    ODOO_DEFAULTS = {
        'type': 'product',                        # Type produit
        'uom_id': 1,                             # Unité : Unité(s)
        'uom_po_id': 1,                          # Unité achat : Unité(s)
        'tracking': 'none',                       # Pas de suivi
        'active': True,                           # Actif
        'sale_ok': True,                          # Vendable
        'purchase_ok': True,                      # Achetable
        'standard_price': 0.0,                    # Prix coût par défaut
        'list_price': 0.0,                        # Prix vente par défaut
    }

    # Catégories ODOO par domaine
    DOMAIN_CATEGORIES = {
        'ELEC': 'Composants Électroniques',
        'MECA': 'Composants Mécaniques',
        'SOFT': 'Logiciels',
        'DOC': 'Documentation'
    }

def _normalize_domain(domain_value: str) -> str:
    """Normaliser la valeur de domaine vers les clés attendues ELEC/MECA."""
    if not isinstance(domain_value, str):
        return 'DOC'
    val = domain_value.strip().upper()
    # Gérer variantes FR/EN
    if val in ('ELEC', 'ELECTRIQUE', 'ÉLECTRIQUE', 'ELECTRICAL'):
        return 'ELEC'
    if val in ('MECA', 'MECANIQUE', 'MÉCANIQUE', 'MECHANICAL'):
        return 'MECA'
    return 'DOC'

def prepare_odoo_export(df_results):
    """Préparer les données pour export ODOO"""

    odoo_data = []

    for _, row in df_results.iterrows():
        domain_raw = row.get('Domain', '')
        domain_norm = _normalize_domain(domain_raw)
        # Données de base
        product_data = {
            'default_code': row['SKU'],
            'name': row['Name'],
            'description': row['Description'] or row['Name'],
            'categ_id': ODOOExportConfig.DOMAIN_CATEGORIES.get(domain_norm, 'Autres'),

            # Fabricant
            'manufacturer_name': row.get('Manufacturer', ''),
            'manufacturer_pname': row.get('Manufacturer_PN', ''),

            # Données techniques
            'x_domain': domain_norm,
            'x_component_type': row.get('ComponentType', ''),
            'x_designator': row.get('Designator', ''),
            'x_quantity_bom': row.get('Quantity', 1),

            # Valeurs par défaut
            **ODOOExportConfig.ODOO_DEFAULTS
        }

        odoo_data.append(product_data)

    return odoo_data

if __name__ == "__main__":
    print("🔧 Configuration ODOO pour export SKU")
    print("📋 Colonnes mappées:", len(ODOOExportConfig.ODOO_COLUMNS))
    print("🏭 Catégories:", list(ODOOExportConfig.DOMAIN_CATEGORIES.keys()))
