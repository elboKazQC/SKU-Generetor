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

        # Alphabet SKU industriel (sans caractères ambigus)
        # Supprime: I, L, O, U, V, 0, 1, 9 pour éviter les confusions
        self.sku_alphabet = "ABCDEFGHJKMNPQRSTWXYZ23456789"
        
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

        # Mapping des types de composants pour le décodage (en français lisible étendu)
        # Format optimisé pour éviter la redondance et clarifier l'action
        self.type_mapping = {
            # Types électriques (lisibles en français - 5-6 lettres)
            "Résistances": "RESIST",
            "Condensateurs": "CONDEN", 
            "Inductances": "INDUCT",
            "Diodes": "DIODES",
            "Transistors": "TRANSI",
            "Circuits intégrés": "CIRCUI",
            "Connecteurs": "CONNEC",
            "Relais": "RELAIS",
            "Fusibles": "FUSIBL",
            "Accessoires de borniers": "BORNIE",
            "Cosses, oeillets, fourchettes": "COSSES",
            "Broches": "BROCHE",
            "Fil": "FILAGE",
            "Boitiers": "BOITIE",
            
            # Types mécaniques optimisés (action + matériau/finition optionnels)
            "Pièces Pliées": "PLIAGE",
            "PIÈCES PLIÉES": "PLIAGE",
            "Pièces Usinées": "USINER", 
            "PIÈCES USINÉES": "USINER",
            "Pièces Découpées": "DECOUP",
            "PIÈCES DÉCOUPÉES LASER": "DECOUP",
            # Boulonnerie : différencier par taille/matériau
            "Boulonnerie": "VISSER",
            "BOULONNERIE": "VISSER",
            "Vis M3": "VISSM3",  # Exemple avec dimension
            "Vis M4": "VISSM4",
            "Vis M5": "VISSM5",
            "Vis M6": "VISSM6",
            "Vis M8": "VISSM8",
            "Boulon M10": "BOULM10",
            "Boulon M12": "BOULM12",
            # Assemblages
            "Assemblage Mécanique": "MONTER",
            "ASSEMBLAGE MÉCANIQUE": "MONTER",
            "Assemblage Final": "FINAL",
            "Sous-assemblage": "SOUSAS",
            # Matériaux avec finition
            "Plastique": "PLASTI",
            "PLASTIQUE": "PLASTI",
            "Aluminium": "ALUMI",
            "Acier": "ACIER",
            "Inox": "INOX",
            "Composantes Mécaniques": "COMPNT",
            "COMPOSANTES MECANIQUES": "COMPNT"
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

    def normalize_text(self, text: str, max_length: int = 6) -> str:
        """Normalise le texte pour le SKU hybride (lisible mais sécurisé) - 5-6 lettres"""
        import unicodedata
        
        if not text:
            return "UNKN"[:max_length]
        
        # Pour les types connus, utiliser directement le mapping français
        text_clean = text.upper().replace(' ', '').replace('È', 'E').replace('É', 'E')
        for french_name, code in self.type_mapping.items():
            french_clean = french_name.upper().replace(' ', '').replace('È', 'E').replace('É', 'E')
            if french_clean in text_clean or text_clean in french_clean:
                return code[:max_length]
        
        # Supprimer les accents et diacritiques
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Convertir en majuscules et garder seulement alphanumériques
        text = ''.join(char.upper() for char in text if char.isalnum())
        
        # Remplacer seulement les caractères vraiment ambigus pour la lisibilité
        replacements = {
            '0': '2',   # 0 -> 2 (éviter confusion avec O)
            '1': '3',   # 1 -> 3 (éviter confusion avec I/l)
            '9': '8',   # 9 -> 8 (éviter confusion avec g)
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Sinon, extraire intelligemment en gardant la lisibilité
        if len(text) <= max_length:
            return text[:max_length]
        
        # Stratégie : premiers caractères de chaque mot important
        words = text.split()
        if len(words) > 1:
            # Prendre la première lettre de chaque mot significatif
            result = ''.join(word[0] for word in words if len(word) > 2)[:max_length]
            if len(result) >= max_length:
                return result[:max_length]
        
        # Sinon priorité aux consonnes pour la lisibilité
        consonants = ''.join(c for c in text if c not in 'AEIUY')
        if len(consonants) >= max_length:
            return consonants[:max_length]
        
        # Compléter avec des voyelles si nécessaire
        vowels = ''.join(c for c in text if c in 'AEIUY')
        result = consonants + vowels
        
        return result[:max_length].ljust(max_length, 'X')

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

    def format_sequence(self, sequence: int) -> str:
        """Formate la séquence en groupes de 4 avec l'alphabet industriel"""
        # Convertir en base avec l'alphabet industriel (28 caractères)
        alphabet = self.sku_alphabet
        base = len(alphabet)
        
        if sequence == 0:
            return "2222"  # Pas de zéro, commence à 2222
        
        # Ajuster la séquence pour commencer à 1
        sequence_adjusted = sequence - 1
        
        # Conversion en base 28 (alphabet industriel)
        result = ""
        temp = sequence_adjusted
        
        # Générer 4 caractères
        for _ in range(4):
            result = alphabet[temp % base] + result
            temp //= base
        
        return result

    def optimize_sku_format(self, domain: str, route_code: str, routing_code: str, type_code: str) -> tuple:
        """
        Optimise le format SKU pour éviter les redondances
        Retourne (route_optimized, routing_optimized, type_optimized)
        """
        
        # Si route et routing sont identiques, simplifier
        if route_code == routing_code:
            # Cas 1: Garder seulement le routing si plus spécifique
            if len(routing_code) >= len(route_code):
                return "STD", routing_code, type_code
            else:
                return route_code, "STD", type_code
        
        # Si le type contient déjà l'information de route/routing, simplifier
        if type_code in route_code or route_code in type_code:
            return "STD", routing_code, type_code
        
        if type_code in routing_code or routing_code in type_code:
            return route_code, "STD", type_code
            
        # Cas spéciaux pour éviter la redondance sémantique
        redundant_pairs = {
            ("BOLT", "BOLT"): ("MECH", "BOLT"),
            ("BEND", "BEND"): ("MECH", "BEND"), 
            ("LASER", "CUT"): ("LASER", "STD"),
            ("CUT", "LASER"): ("LASER", "STD"),
            ("ASS", "ASM"): ("ASS", "STD"),
            ("ASM", "ASS"): ("ASM", "STD")
        }
        
        pair_key = (route_code, routing_code)
        if pair_key in redundant_pairs:
            return redundant_pairs[pair_key][0], redundant_pairs[pair_key][1], type_code
            
        # Pas de redondance détectée, garder tel quel
        return route_code, routing_code, type_code

    def _validate_component(self, component: Component) -> bool:
        """
        Valide qu'un composant a les informations minimales requises
        pour générer un SKU valide
        """
        # Vérifier que le nom n'est pas vide ou juste des espaces
        if not component.name or not component.name.strip():
            logger.warning(f"Composant rejeté: nom vide ou manquant")
            return False
            
        # Vérifier que le nom n'est pas un placeholder générique
        invalid_names = ['nan', 'none', 'null', '', '(vide)', 'empty', 'unnamed']
        name_lower = component.name.lower().strip()
        if name_lower in invalid_names:
            logger.warning(f"Composant rejeté: nom invalide '{component.name}'")
            return False
            
        # Vérifier que la description n'est pas vide (peut être moins strict)
        if not component.description or not component.description.strip():
            logger.warning(f"Composant '{component.name}': description vide")
            # On peut permettre une description vide mais on l'indique
            component.description = "Description non fournie"
            
        # Vérifier que le domaine est valide
        if not component.domain or component.domain not in ['ELEC', 'MECA']:
            logger.warning(f"Composant '{component.name}': domaine invalide '{component.domain}'")
            return False
            
        # Vérifier que le type de composant n'est pas vide
        if not component.component_type or not component.component_type.strip():
            logger.warning(f"Composant '{component.name}': type de composant manquant")
            return False
            
        # Vérifier que le type n'est pas un placeholder
        type_lower = component.component_type.lower().strip()
        if type_lower in invalid_names:
            logger.warning(f"Composant '{component.name}': type invalide '{component.component_type}'")
            return False

        return True

    def generate_sku(self, component: Component) -> str:
        """Génère un SKU optimisé pour un composant"""
        
        # Validation des champs obligatoires pour éviter les SKU vides
        if not self._validate_component(component):
            logger.warning(f"Composant invalide ignoré: {component.name} - {component.description}")
            raise ValueError(f"Composant invalide: champs obligatoires manquants")

        # Vérifier si le composant existe déjà
        existing_sku = self.get_existing_sku(component)
        if existing_sku:
            logger.info(f"Composant existant trouvé: {existing_sku}")
            return existing_sku

        # Générer les codes de base
        route_code = self.get_route_code(component.component_type, component.domain)
        routing_code = self.get_routing_code(component.component_type)
        type_code = self.normalize_text(component.component_type, 6)

        # Optimiser le format pour éviter les redondances
        route_opt, routing_opt, type_opt = self.optimize_sku_format(
            component.domain, route_code, routing_code, type_code
        )

        # Obtenir le numéro de séquence avec les codes optimisés
        sequence = self.get_next_sequence(component.domain, route_opt, routing_opt, type_opt)

        # Formater la séquence avec l'alphabet industriel
        sequence_code = self.format_sequence(sequence)

        # Construire le SKU optimisé
        sku = f"{component.domain}-{route_opt}-{routing_opt}-{type_opt}-{sequence_code}"

        # Sauvegarder dans la base de données
        self.save_component(component, sku)

        logger.info(f"Nouveau SKU optimisé généré: {sku}")
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
