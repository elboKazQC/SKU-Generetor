#!/usr/bin/env python3
"""
Générateur de SKU industriel avec logique de route et routing
Développé pour Noovelia par GitHub Copilot
"""

import pandas as pd
import sqlite3
import hashlib
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Component:
    """Classe représentant un composant avec ses attributs"""
    name: str
    description: str
    domain: str  # ELEC ou MECA
    component_type: str
    route: str
    routing: str
    manufacturer: Optional[str] = None
    manufacturer_part: Optional[str] = None
    quantity: Optional[float] = None
    designator: Optional[str] = None

class SKUGenerator:
    """Générateur de SKU avec logique industrielle"""

    def __init__(self, db_path: str = "sku_database.db"):
        self.db_path = db_path
        self.init_database()

        # Mapping des routes et routings basé sur vos données
        self.route_mapping = {
            # Routes électriques
            "Assemblage": "ASS",
            "Connecteurs": "CONN",
            "Borniers": "TERM",
            "Communication": "COMM",
            "Contrôleurs": "CTRL",
            "Alimentation": "POWER",
            "Moteurs": "MOTOR",

            # Routes mécaniques
            "ASSEMBLAGE MÉCANIQUE": "ASS",
            "ASSEMBLAGE SOUDÉ": "WELD",
            "PIÈCES USINÉES": "MACH",
            "PIÈCES PLIÉES": "BEND",
            "PIÈCES DÉCOUPÉES LASER": "LASER",
            "BOULONNERIE": "BOLT",
            "PLASTIQUE": "PLAST"
        }

        self.routing_mapping = {
            # Routings électriques
            "Assemblage": "ASM",
            "Cosses, oeillets, fourchettes": "TERM",
            "Boitiers": "ENCL",
            "Fusibles": "FUSE",
            "Broches": "PIN",
            "Fil": "WIRE",

            # Routings mécaniques
            "BOULONNERIE": "BOLT",
            "PIÈCES PLIÉES": "BEND",
            "ASSEMBLAGE MÉCANIQUE": "MECH",
            "COMPOSANTES MECANIQUES": "COMP",
            "PIÈCES DÉCOUPÉES LASER": "CUT",
            "PIÈCES USINÉES": "MILL",
            "PLASTIQUE (UHMW, LEXAN, ...)": "POLY"
        }

        # Mapping des types de composants pour le décodage
        self.type_mapping = {
            # Types électriques
            "Résistances": "RES",
            "Condensateurs": "CAP",
            "Inductances": "IND",
            "Diodes": "DIO",
            "Transistors": "TRA",
            "Circuits intégrés": "IC",
            "Connecteurs": "CON",
            "Relais": "REL",
            "Fusibles": "FUS",
            "Accessoires de borniers": "TERM",

            # Types mécaniques
            "Pièces Pliées": "121P",
            "Pièces Usinées": "122U",
            "Pièces Découpées": "123D",
            "Boulonnerie": "124B",
            "Assemblage Mécanique": "125A",
            "Plastique": "126P"
        }

    def init_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                domain TEXT NOT NULL,
                component_type TEXT,
                route TEXT,
                routing TEXT,
                manufacturer TEXT,
                manufacturer_part TEXT,
                component_hash TEXT UNIQUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sku_counters (
                domain TEXT,
                route TEXT,
                routing TEXT,
                type_code TEXT,
                counter INTEGER DEFAULT 0,
                PRIMARY KEY (domain, route, routing, type_code)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Base de données initialisée")

    def normalize_text(self, text: str, max_length: int = 4) -> str:
        """Normalise le texte pour le SKU"""
        if not text:
            return "UNK"

        # Nettoyer et normaliser
        text = re.sub(r'[^\w\s-]', '', str(text).upper())
        text = re.sub(r'\s+', '', text)

        # Extraire les caractères significatifs
        if len(text) <= max_length:
            return text.ljust(max_length, 'X')

        # Extraire consonnes puis voyelles si nécessaire
        consonants = re.sub(r'[AEIOU]', '', text)
        if len(consonants) >= max_length:
            return consonants[:max_length]

        return text[:max_length]

    def get_route_code(self, component_type: str, domain: str) -> str:
        """Détermine le code de route basé sur le type de composant"""
        for key, code in self.route_mapping.items():
            if key.upper() in component_type.upper():
                return code

        # Route par défaut selon le domaine
        return "ELEC" if domain == "ELEC" else "MECA"

    def get_routing_code(self, component_type: str) -> str:
        """Détermine le code de routing basé sur le type de composant"""
        for key, code in self.routing_mapping.items():
            if key.upper() in component_type.upper():
                return code

        return "STD"  # Routing standard par défaut

    def create_component_hash(self, component: Component) -> str:
        """Crée un hash unique pour identifier les composants similaires"""
        hash_string = f"{component.name}_{component.description}_{component.component_type}_{component.manufacturer}_{component.manufacturer_part}"
        return hashlib.md5(hash_string.encode()).hexdigest()[:8]

    def get_existing_sku(self, component: Component) -> Optional[str]:
        """Vérifie si un composant similaire existe déjà"""
        component_hash = self.create_component_hash(component)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT sku FROM components WHERE component_hash = ?
        ''', (component_hash,))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def get_next_sequence(self, domain: str, route: str, routing: str, type_code: str) -> int:
        """Obtient le prochain numéro de séquence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT counter FROM sku_counters
            WHERE domain = ? AND route = ? AND routing = ? AND type_code = ?
        ''', (domain, route, routing, type_code))

        result = cursor.fetchone()

        if result:
            new_counter = result[0] + 1
            cursor.execute('''
                UPDATE sku_counters
                SET counter = ?
                WHERE domain = ? AND route = ? AND routing = ? AND type_code = ?
            ''', (new_counter, domain, route, routing, type_code))
        else:
            new_counter = 1
            cursor.execute('''
                INSERT INTO sku_counters (domain, route, routing, type_code, counter)
                VALUES (?, ?, ?, ?, ?)
            ''', (domain, route, routing, type_code, new_counter))

        conn.commit()
        conn.close()

        return new_counter

    def generate_sku(self, component: Component) -> str:
        """Génère un SKU pour un composant"""

        # Vérifier si le composant existe déjà
        existing_sku = self.get_existing_sku(component)
        if existing_sku:
            logger.info(f"Composant existant trouvé: {existing_sku}")
            return existing_sku

        # Générer les codes
        route_code = self.get_route_code(component.component_type, component.domain)
        routing_code = self.get_routing_code(component.component_type)
        type_code = self.normalize_text(component.component_type, 4)

        # Obtenir le numéro de séquence
        sequence = self.get_next_sequence(component.domain, route_code, routing_code, type_code)

        # Construire le SKU
        sku = f"{component.domain}-{route_code}-{routing_code}-{type_code}-{sequence:05d}"

        # Sauvegarder dans la base de données
        self.save_component(component, sku)

        logger.info(f"Nouveau SKU généré: {sku}")
        return sku

    def save_component(self, component: Component, sku: str):
        """Sauvegarde le composant dans la base de données"""
        component_hash = self.create_component_hash(component)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO components (
                sku, name, description, domain, component_type,
                route, routing, manufacturer, manufacturer_part, component_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sku, component.name, component.description, component.domain,
            component.component_type, component.route, component.routing,
            component.manufacturer, component.manufacturer_part, component_hash
        ))

        conn.commit()
        conn.close()

    def search_component_by_sku(self, sku: str) -> Optional[Dict]:
        """Rechercher un composant par son SKU"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, sku, domain, route, routing, component_type,
                   manufacturer, manufacturer_part, description, created_date
            FROM components
            WHERE sku = ?
        """, (sku.upper(),))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'nom': result[0],
                'sku': result[1],
                'domaine': result[2],
                'route': result[3],
                'routing': result[4],
                'type': result[5],
                'fabricant': result[6],
                'ref_fabricant': result[7],
                'description': result[8],
                'date_creation': result[9]
            }
        return None

    def find_similar_components(self, domain: str, component_type: str) -> List[Dict]:
        """Trouver des composants similaires par domaine et type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, sku, domain, route, routing, component_type
            FROM components
            WHERE domain = ? AND component_type = ?
            ORDER BY created_date DESC
            LIMIT 20
        """, (domain, component_type))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'nom': result[0],
                'sku': result[1],
                'domaine': result[2],
                'route': result[3],
                'routing': result[4],
                'type': result[5]
            }
            for result in results
        ]

    def search_partial_sku(self, partial_sku: str) -> List[Dict]:
        """Rechercher des SKU qui contiennent une partie du SKU donné"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Recherche avec LIKE pour trouver des SKU similaires
        search_pattern = f"%{partial_sku.upper()}%"

        cursor.execute("""
            SELECT name, sku, domain, route, routing, component_type
            FROM components
            WHERE sku LIKE ?
            ORDER BY sku
            LIMIT 15
        """, (search_pattern,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'nom': result[0],
                'sku': result[1],
                'domaine': result[2],
                'route': result[3],
                'routing': result[4],
                'type': result[5]
            }
            for result in results
        ]

    def get_all_skus(self, limit: int = 100) -> List[Dict]:
        """Récupérer tous les SKU avec pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, sku, domain, component_type, created_date
            FROM components
            ORDER BY created_date DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'nom': result[0],
                'sku': result[1],
                'domaine': result[2],
                'type': result[3],
                'date_creation': result[4]
            }
            for result in results
        ]

    def decode_sku_parts(self, sku: str) -> Dict[str, str]:
        """Décoder les parties d'un SKU avec leurs significations"""
        parts = sku.split('-')
        if len(parts) != 5:
            return {}

        domain_code, route_code, routing_code, type_code, sequence = parts

        # Mapping inverse pour les domaines
        domain_meaning = {
            'ELEC': 'Électrique',
            'MECA': 'Mécanique'
        }.get(domain_code, domain_code)

        # Mapping inverse pour les routes
        route_meaning = {}
        for full_name, code in self.route_mapping.items():
            route_meaning[code] = full_name

        # Mapping inverse pour les routings
        routing_meaning = {}
        for full_name, code in self.routing_mapping.items():
            routing_meaning[code] = full_name

        # Mapping inverse pour les types
        type_meaning = {}
        for full_name, code in self.type_mapping.items():
            type_meaning[code] = full_name

        return {
            'domaine_code': domain_code,
            'domaine_nom': domain_meaning,
            'route_code': route_code,
            'route_nom': route_meaning.get(route_code, route_code),
            'routing_code': routing_code,
            'routing_nom': routing_meaning.get(routing_code, routing_code),
            'type_code': type_code,
            'type_nom': type_meaning.get(type_code, type_code),
            'sequence': sequence
        }

    def get_process_description(self, domain: str, route: str, routing: str) -> str:
        """Obtenir une description du processus basé sur le domaine, route et routing"""
        if domain == "ELEC":
            if route == "ASS" and routing == "SMT":
                return "Assemblage par montage en surface (SMT)"
            elif route == "ASS" and routing == "THT":
                return "Assemblage par technologie traversante (THT)"
            elif route == "ASS":
                return "Assemblage électrique"
            elif route == "TEST":
                return "Test et validation électrique"
            elif route == "PROG":
                return "Programmation de composants"
            else:
                return f"Processus électrique ({route} → {routing})"
        elif domain == "MECA":
            if route == "USIN" and routing == "FRAI":
                return "Usinage par fraisage"
            elif route == "USIN" and routing == "TOUR":
                return "Usinage par tournage"
            elif route == "BEND" and routing == "BEND":
                return "Pliage de tôlerie"
            elif route == "ASS":
                return "Assemblage mécanique"
            elif route == "CTRL":
                return "Contrôle qualité mécanique"
            else:
                return f"Processus mécanique ({route} → {routing})"
        else:
            return f"Processus {domain} ({route} → {routing})"

if __name__ == "__main__":
    # Test du générateur
    generator = SKUGenerator()

    # Test avec un composant électrique
    comp_elec = Component(
        name="D-ST 2,5",
        description="Accessoires de borniers",
        domain="ELEC",
        component_type="Accessoires de borniers",
        route="",
        routing="",
        manufacturer="Phoenix Contact"
    )

    sku = generator.generate_sku(comp_elec)
    print(f"SKU généré: {sku}")
