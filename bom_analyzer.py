#!/usr/bin/env python3
"""
Script pour comparer et analyser les BOM avec gestion des SKU existants
"""

import pandas as pd
import sqlite3
from sku_generator import SKUGenerator, Component
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BOMComparator:
    """Comparateur de BOM pour détecter les nouveaux composants et ceux existants"""

    def __init__(self, sku_generator: SKUGenerator):
        self.sku_generator = sku_generator

    def analyze_new_bom(self, file_path: str) -> dict:
        """Analyse un nouveau BOM et compare avec les composants existants"""
        logger.info(f"Analyse du nouveau BOM: {file_path}")

        # Lire le nouveau BOM
        excel_data = pd.read_excel(file_path, sheet_name=None)

        results = {
            'nouveau': 0,
            'existant': 0,
            'details': {'Électrique': {}, 'Mécanique': {}}
        }

        # Analyser BOM Électrique
        if 'BOM Électrique' in excel_data:
            elec_analysis = self._analyze_sheet(excel_data['BOM Électrique'], "ELEC")
            results['details']['Électrique'] = elec_analysis
            results['nouveau'] += elec_analysis['nouveau']
            results['existant'] += elec_analysis['existant']

        # Analyser BOM Mécanique
        if 'BOM Mécanique' in excel_data:
            meca_analysis = self._analyze_sheet_meca(excel_data['BOM Mécanique'], "MECA")
            results['details']['Mécanique'] = meca_analysis
            results['nouveau'] += meca_analysis['nouveau']
            results['existant'] += meca_analysis['existant']

        return results

    def _analyze_sheet(self, df: pd.DataFrame, domain: str) -> dict:
        """Analyse une feuille électrique"""
        nouveau = 0
        existant = 0
        composants_nouveaux = []
        composants_existants = []

        for _, row in df.iterrows():
            component = Component(
                name=str(row.get('Name', '')),
                description=str(row.get('Description', '')),
                domain=domain,
                component_type=str(row.get('ComponentType', '')),
                route="",
                routing="",
                manufacturer=str(row.get('Manufacturer', '')),
                manufacturer_part=str(row.get('Manufacturer PN', ''))
            )

            existing_sku = self.sku_generator.get_existing_sku(component)

            if existing_sku:
                existant += 1
                composants_existants.append({
                    'nom': component.name,
                    'sku_existant': existing_sku,
                    'type': component.component_type
                })
            else:
                nouveau += 1
                composants_nouveaux.append({
                    'nom': component.name,
                    'type': component.component_type,
                    'description': component.description
                })

        return {
            'nouveau': nouveau,
            'existant': existant,
            'composants_nouveaux': composants_nouveaux,
            'composants_existants': composants_existants
        }

    def _analyze_sheet_meca(self, df: pd.DataFrame, domain: str) -> dict:
        """Analyse une feuille mécanique"""
        nouveau = 0
        existant = 0
        composants_nouveaux = []
        composants_existants = []

        for _, row in df.iterrows():
            component = Component(
                name=str(row.get('No. de pièce', '')),
                description=str(row.get('Description Française', '')),
                domain=domain,
                component_type=str(row.get('Type', '')),
                route="",
                routing="",
                manufacturer=str(row.get('Manufacturier', '')),
                manufacturer_part=str(row.get('No. de pièce', ''))
            )

            existing_sku = self.sku_generator.get_existing_sku(component)

            if existing_sku:
                existant += 1
                composants_existants.append({
                    'nom': component.name,
                    'sku_existant': existing_sku,
                    'type': component.component_type
                })
            else:
                nouveau += 1
                composants_nouveaux.append({
                    'nom': component.name,
                    'type': component.component_type,
                    'description': component.description
                })

        return {
            'nouveau': nouveau,
            'existant': existant,
            'composants_nouveaux': composants_nouveaux,
            'composants_existants': composants_existants
        }

    def get_database_stats(self) -> dict:
        """Obtient les statistiques de la base de données"""
        conn = sqlite3.connect(self.sku_generator.db_path)
        cursor = conn.cursor()

        # Total des composants
        cursor.execute("SELECT COUNT(*) FROM components")
        total = cursor.fetchone()[0]

        # Par domaine
        cursor.execute("SELECT domain, COUNT(*) FROM components GROUP BY domain")
        by_domain = dict(cursor.fetchall())

        # Par route
        cursor.execute("SELECT route, COUNT(*) FROM components GROUP BY route ORDER BY COUNT(*) DESC")
        by_route = dict(cursor.fetchall())

        # Par routing
        cursor.execute("SELECT routing, COUNT(*) FROM components GROUP BY routing ORDER BY COUNT(*) DESC")
        by_routing = dict(cursor.fetchall())

        conn.close()

        return {
            'total': total,
            'par_domaine': by_domain,
            'par_route': by_route,
            'par_routing': by_routing
        }

def main():
    """Fonction principale pour analyser les BOM"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialiser le générateur
    generator = SKUGenerator()
    comparator = BOMComparator(generator)

    # Analyser le fichier actuel (simulation d'un nouveau BOM)
    file_path = "(V2.1) BOM unifié électrique-mécanique.xlsx"

    if not Path(file_path).exists():
        print(f"Fichier non trouvé: {file_path}")
        return

    print("="*60)
    print("ANALYSE DE BOM AVEC DETECTION DES COMPOSANTS EXISTANTS")
    print("="*60)

    # Obtenir les stats de la base de données
    stats = comparator.get_database_stats()
    print(f"\n📊 STATISTIQUES BASE DE DONNÉES")
    print(f"Total composants: {stats['total']}")
    print(f"Par domaine: {stats['par_domaine']}")
    print(f"\nTop 5 routes:")
    for route, count in list(stats['par_route'].items())[:5]:
        print(f"  {route}: {count}")
    print(f"\nTop 5 routings:")
    for routing, count in list(stats['par_routing'].items())[:5]:
        print(f"  {routing}: {count}")

    # Simuler l'analyse d'un nouveau BOM (en réalité c'est le même fichier)
    print(f"\n🔍 ANALYSE NOUVEAU BOM: {file_path}")
    analysis = comparator.analyze_new_bom(file_path)

    print(f"\n📈 RÉSULTATS:")
    print(f"Composants NOUVEAUX: {analysis['nouveau']}")
    print(f"Composants EXISTANTS: {analysis['existant']}")
    print(f"Total analysé: {analysis['nouveau'] + analysis['existant']}")

    # Détails par domaine
    for domain, details in analysis['details'].items():
        if details:
            print(f"\n🔧 {domain.upper()}:")
            print(f"  Nouveaux: {details['nouveau']}")
            print(f"  Existants: {details['existant']}")

            if details['composants_existants'] and len(details['composants_existants']) > 0:
                print(f"  Exemples de composants existants:")
                for comp in details['composants_existants'][:3]:
                    print(f"    - {comp['nom']} → {comp['sku_existant']}")

    print(f"\n💾 Base de données: {generator.db_path}")
    print("✅ Analyse terminée")

if __name__ == "__main__":
    main()
