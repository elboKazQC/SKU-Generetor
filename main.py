#!/usr/bin/env python3
"""
Script principal pour traiter les fichiers BOM et générer les SKU
"""

import pandas as pd
import sys
from pathlib import Path
from sku_generator import SKUGenerator, Component
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class BOMProcessor:
    """Processeur de fichiers BOM"""

    def __init__(self, sku_generator: SKUGenerator):
        self.sku_generator = sku_generator

    def process_electrical_bom(self, df: pd.DataFrame) -> pd.DataFrame:
        """Traite le BOM électrique"""
        results = []
        skipped_count = 0

        for line_num, (idx, row) in enumerate(df.iterrows(), start=2):
            try:
                component = Component(
                    name=str(row.get('Name', '')),
                    description=str(row.get('Description', '')),
                    domain="ELEC",
                    component_type=str(row.get('ComponentType', '')),
                    route="",  # Sera calculé automatiquement
                    routing="",  # Sera calculé automatiquement
                    manufacturer=str(row.get('Manufacturer', '')),
                    manufacturer_part=str(row.get('Manufacturer PN', '')),
                    quantity=row.get('Quantity'),
                    designator=str(row.get('Designator', ''))
                )

                sku = self.sku_generator.generate_sku(component)

                results.append({
                    'SKU': sku,
                    'Name': component.name,
                    'Description': component.description,
                    'ComponentType': component.component_type,
                    'Manufacturer': component.manufacturer,
                    'Manufacturer_PN': component.manufacturer_part,
                    'Quantity': component.quantity,
                    'Designator': component.designator,
                    'Domain': 'ÉLECTRIQUE'
                })

            except ValueError as e:
                skipped_count += 1
                logger.warning(f"Composant électrique ignoré (ligne {line_num}): {e}")
                continue
            except Exception as e:
                skipped_count += 1
                logger.error(f"Erreur lors du traitement du composant électrique (ligne {line_num}): {e}")
                continue

        if skipped_count > 0:
            logger.info(f"🚨 {skipped_count} composants électriques ignorés (items vides ou invalides)")

        return pd.DataFrame(results)

    def extract_electrical_components(self, df: pd.DataFrame) -> List[Component]:
        """Extrait les composants électriques sans générer les SKU"""
        components = []
        skipped_count = 0

        for line_num, (idx, row) in enumerate(df.iterrows(), start=2):
            try:
                component = Component(
                    name=str(row.get('Name', '')),
                    description=str(row.get('Description', '')),
                    domain="ELEC",
                    component_type=str(row.get('ComponentType', '')),
                    route="",  # Sera calculé automatiquement
                    routing="",  # Sera calculé automatiquement
                    manufacturer=str(row.get('Manufacturer', '')),
                    manufacturer_part=str(row.get('Manufacturer PN', '')),
                    quantity=row.get('Quantity'),
                    designator=str(row.get('Designator', ''))
                )

                # Valider le composant sans générer le SKU
                if self.sku_generator.validate_component(component):
                    components.append(component)
                else:
                    skipped_count += 1
            
            except Exception as e:
                skipped_count += 1
                logger.warning(f"Composant électrique ignoré (ligne {line_num}): {e}")
                continue

        if skipped_count > 0:
            logger.info(f"🚨 {skipped_count} composants électriques ignorés (items vides ou invalides)")

        return components

    def extract_mechanical_components(self, df: pd.DataFrame) -> List[Component]:
        """Extrait les composants mécaniques sans générer les SKU"""
        components = []
        skipped_count = 0

        for line_num, (idx, row) in enumerate(df.iterrows(), start=2):
            try:
                component = Component(
                    name=str(row.get('No. de pièce', '')),
                    description=str(row.get('Description Française', '')),
                    domain="MECA",
                    component_type=str(row.get('Type', '')),
                    route="",  # Sera calculé automatiquement
                    routing="",  # Sera calculé automatiquement
                    manufacturer=str(row.get('Manufacturier', '')),
                    manufacturer_part=str(row.get('No. de pièce', '')),
                    quantity=row.get('QTE TOTALE')
                )

                # Valider le composant sans générer le SKU
                if self.sku_generator.validate_component(component):
                    components.append(component)
                else:
                    skipped_count += 1

            except Exception as e:
                skipped_count += 1
                logger.warning(f"Composant mécanique ignoré (ligne {line_num}): {e}")
                continue

        if skipped_count > 0:
            logger.info(f"🚨 {skipped_count} composants mécaniques ignorés (items vides ou invalides)")

        return components

    def generate_skus_for_selected_components(self, components_by_domain: Dict[str, List[Component]]) -> dict:
        """Génère les SKU pour les composants sélectionnés"""
        results = {}

        for domain, components in components_by_domain.items():
            if domain == "ELEC":
                results["Électrique"] = self._process_selected_electrical_components(components)
            elif domain == "MECA":
                results["Mécanique"] = self._process_selected_mechanical_components(components)

        return results

    def _process_selected_electrical_components(self, components: List[Component]) -> pd.DataFrame:
        """Traite les composants électriques sélectionnés"""
        results = []

        for component in components:
            try:
                sku = self.sku_generator.generate_sku(component)

                results.append({
                    'SKU': sku,
                    'Name': component.name,
                    'Description': component.description,
                    'ComponentType': component.component_type,
                    'Manufacturer': component.manufacturer,
                    'Manufacturer_PN': component.manufacturer_part,
                    'Quantity': component.quantity,
                    'Designator': component.designator,
                    'Domain': 'ÉLECTRIQUE'
                })
            
            except Exception as e:
                logger.error(f"Erreur lors de la génération du SKU pour {component.name}: {e}")
                continue

        return pd.DataFrame(results)

    def _process_selected_mechanical_components(self, components: List[Component]) -> pd.DataFrame:
        """Traite les composants mécaniques sélectionnés"""
        results = []

        for component in components:
            try:
                sku = self.sku_generator.generate_sku(component)

                results.append({
                    'SKU': sku,
                    'Name': component.name,
                    'Description': component.description,
                    'ComponentType': component.component_type,
                    'Manufacturer': component.manufacturer,
                    'Manufacturer_PN': component.manufacturer_part,
                    'Quantity': component.quantity,
                    'Domain': 'MÉCANIQUE'
                })

            except Exception as e:
                logger.error(f"Erreur lors de la génération du SKU pour {component.name}: {e}")
                continue

        return pd.DataFrame(results)

    def extract_components_from_bom(self, file_path: str) -> Dict[str, List[Component]]:
        """Extrait tous les composants d'un fichier BOM sans générer les SKU"""
        logger.info(f"Extraction des composants du fichier: {file_path}")

        try:
            # Lire toutes les feuilles
            excel_data = pd.read_excel(file_path, sheet_name=None)

            components_by_domain = {}

            # Extraire les composants électriques
            if 'BOM Électrique' in excel_data:
                logger.info("Extraction des composants électriques...")
                elec_components = self.extract_electrical_components(excel_data['BOM Électrique'])
                if elec_components:
                    components_by_domain['ELEC'] = elec_components

            # Extraire les composants mécaniques
            if 'BOM Mécanique' in excel_data:
                logger.info("Extraction des composants mécaniques...")
                meca_components = self.extract_mechanical_components(excel_data['BOM Mécanique'])
                if meca_components:
                    components_by_domain['MECA'] = meca_components

            total_components = sum(len(components) for components in components_by_domain.values())
            logger.info(f"Total des composants valides extraits: {total_components}")

            return components_by_domain

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des composants: {e}")
            raise

    def process_mechanical_bom(self, df: pd.DataFrame) -> pd.DataFrame:
        """Traite le BOM mécanique"""
        results = []
        skipped_count = 0

        for line_num, (idx, row) in enumerate(df.iterrows(), start=2):
            try:
                component = Component(
                    name=str(row.get('No. de pièce', '')),
                    description=str(row.get('Description Française', '')),
                    domain="MECA",
                    component_type=str(row.get('Type', '')),
                    route="",  # Sera calculé automatiquement
                    routing="",  # Sera calculé automatiquement
                    manufacturer=str(row.get('Manufacturier', '')),
                    manufacturer_part=str(row.get('No. de pièce', '')),
                    quantity=row.get('QTE TOTALE')
                )

                sku = self.sku_generator.generate_sku(component)

                results.append({
                    'SKU': sku,
                    'Name': component.name,
                    'Description': component.description,
                    'ComponentType': component.component_type,
                    'Manufacturer': component.manufacturer,
                    'Manufacturer_PN': component.manufacturer_part,
                    'Quantity': component.quantity,
                    'Domain': 'MÉCANIQUE'
                })

            except ValueError as e:
                skipped_count += 1
                logger.warning(f"Composant mécanique ignoré (ligne {line_num}): {e}")
                continue
            except Exception as e:
                skipped_count += 1
                logger.error(f"Erreur lors du traitement du composant mécanique (ligne {line_num}): {e}")
                continue

        if skipped_count > 0:
            logger.info(f"🚨 {skipped_count} composants mécaniques ignorés (items vides ou invalides)")

        return pd.DataFrame(results)

    def process_bom_file(self, file_path: str) -> dict:
        """Traite un fichier BOM complet"""
        logger.info(f"Traitement du fichier: {file_path}")

        try:
            # Lire toutes les feuilles
            excel_data = pd.read_excel(file_path, sheet_name=None)

            results = {}

            # Traiter BOM Électrique
            if 'BOM Électrique' in excel_data:
                logger.info("Traitement BOM Électrique...")
                elec_results = self.process_electrical_bom(excel_data['BOM Électrique'])
                results['Électrique'] = elec_results
                logger.info(f"BOM Électrique: {len(elec_results)} composants traités")

            # Traiter BOM Mécanique
            if 'BOM Mécanique' in excel_data:
                logger.info("Traitement BOM Mécanique...")
                meca_results = self.process_mechanical_bom(excel_data['BOM Mécanique'])
                results['Mécanique'] = meca_results
                logger.info(f"BOM Mécanique: {len(meca_results)} composants traités")

            return results

        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier: {e}")
            raise

    def export_results(self, results: dict, output_file: str):
        """Exporte les résultats vers un fichier Excel"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for domain, df in results.items():
                df.to_excel(writer, sheet_name=f"SKU_{domain}", index=False)

        logger.info(f"Résultats exportés vers: {output_file}")

def main():
    """Fonction principale"""
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Fichier d'entrée
    input_file = "(V2.1) BOM unifié électrique-mécanique.xlsx"
    output_file = "SKU_Results.xlsx"

    if not Path(input_file).exists():
        logger.error(f"Fichier non trouvé: {input_file}")
        sys.exit(1)

    try:
        # Initialiser le générateur de SKU
        generator = SKUGenerator()
        processor = BOMProcessor(generator)

        # Traiter le fichier BOM
        results = processor.process_bom_file(input_file)

        # Exporter les résultats
        processor.export_results(results, output_file)

        # Afficher un résumé
        print("\n" + "="*50)
        print("RÉSUMÉ DU TRAITEMENT")
        print("="*50)

        total_components = 0
        for domain, df in results.items():
            count = len(df)
            total_components += count
            print(f"{domain}: {count} composants")

            # Afficher quelques exemples de SKU
            print(f"Exemples de SKU {domain}:")
            for i, sku in enumerate(df['SKU'].head(3)):
                print(f"  - {sku}")
            print()

        print(f"TOTAL: {total_components} composants traités")
        print(f"Résultats sauvegardés dans: {output_file}")
        print("Base de données SKU: sku_database.db")

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
