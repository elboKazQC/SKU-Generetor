#!/usr/bin/env python3
"""
Configuration du générateur de SKU
Modifiez ce fichier pour adapter le système à vos besoins
"""

# Configuration des domaines
DOMAINS = {
    "ELEC": "Électrique",
    "MECA": "Mécanique",
    "SOFT": "Software",  # Exemple d'extension
    "PACK": "Packaging"  # Exemple d'extension
}

# Configuration des routes électriques
ELECTRICAL_ROUTES = {
    "Assemblage": "ASS",
    "Connecteurs": "CONN",
    "Borniers": "TERM",
    "Communication": "COMM",
    "Contrôleurs": "CTRL",
    "Alimentation": "POWER",
    "Moteurs": "MOTOR",
    "Capteurs": "SENS",
    "Actionneurs": "ACT"
}

# Configuration des routes mécaniques
MECHANICAL_ROUTES = {
    "ASSEMBLAGE MÉCANIQUE": "ASS",
    "ASSEMBLAGE SOUDÉ": "WELD",
    "PIÈCES USINÉES": "MACH",
    "PIÈCES PLIÉES": "BEND",
    "PIÈCES DÉCOUPÉES LASER": "LASER",
    "BOULONNERIE": "BOLT",
    "PLASTIQUE": "PLAST",
    "TÔLERIE": "SHEET"
}

# Configuration des routings électriques
ELECTRICAL_ROUTINGS = {
    "Assemblage": "ASM",
    "Cosses, oeillets, fourchettes": "TERM",
    "Boitiers": "ENCL",
    "Fusibles": "FUSE",
    "Broches": "PIN",
    "Fil": "WIRE",
    "Circuit imprimé": "PCB",
    "Composants CMS": "SMD"
}

# Configuration des routings mécaniques
MECHANICAL_ROUTINGS = {
    "BOULONNERIE": "BOLT",
    "PIÈCES PLIÉES": "BEND",
    "ASSEMBLAGE MÉCANIQUE": "MECH",
    "COMPOSANTES MECANIQUES": "COMP",
    "PIÈCES DÉCOUPÉES LASER": "CUT",
    "PIÈCES USINÉES": "MILL",
    "PLASTIQUE (UHMW, LEXAN, ...)": "POLY",
    "SOUDURE": "WELD"
}

# Configuration du format des SKU
SKU_FORMAT = {
    "separator": "-",           # Séparateur entre les parties
    "domain_length": 4,         # Longueur du code domaine
    "route_length": 4,          # Longueur du code route
    "routing_length": 4,        # Longueur du code routing
    "type_length": 4,           # Longueur du code type
    "sequence_padding": 5       # Nombre de zéros pour la séquence
}

# Configuration de la base de données
DATABASE_CONFIG = {
    "name": "sku_database.db",
    "backup_interval": 100,     # Sauvegarder après N insertions
    "auto_backup": True
}

# Configuration des logs
LOGGING_CONFIG = {
    "level": "INFO",            # DEBUG, INFO, WARNING, ERROR
    "file": "sku_generator.log",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
}

# Configuration des exports
EXPORT_CONFIG = {
    "excel_format": "xlsx",
    "include_metadata": True,   # Inclure les métadonnées dans l'export
    "sheet_names": {
        "electrical": "SKU_Électrique",
        "mechanical": "SKU_Mécanique",
        "summary": "Résumé"
    }
}

# Règles de validation
VALIDATION_RULES = {
    "min_name_length": 2,       # Longueur minimale du nom
    "max_name_length": 100,     # Longueur maximale du nom
    "required_fields": ["name", "domain", "component_type"],
    "forbidden_characters": ["<", ">", "|", ":", "*", "?", '"', "/", "\\"]
}

# Messages et textes
MESSAGES = {
    "welcome": "Générateur de SKU Industriel - Noovelia",
    "success_generation": "SKU généré avec succès",
    "error_duplicate": "Composant similaire détecté",
    "info_existing": "SKU existant réutilisé"
}

# Configuration des types de composants personnalisés
CUSTOM_COMPONENT_TYPES = {
    # Électriques
    "ELEC": {
        "Microcontrôleurs": "MCU",
        "Capteurs de température": "TEMP",
        "LEDs": "LED",
        "Écrans": "DISP"
    },
    # Mécaniques
    "MECA": {
        "Roulements": "BEAR",
        "Joints": "SEAL",
        "Ressorts": "SPRI",
        "Engrenages": "GEAR"
    }
}

# Configuration avancée pour la détection des doublons
DUPLICATE_DETECTION = {
    "hash_fields": ["name", "description", "component_type", "manufacturer"],
    "similarity_threshold": 0.85,  # Seuil de similarité (0-1)
    "ignore_case": True,
    "ignore_whitespace": True
}

def get_route_mapping():
    """Retourne le mapping complet des routes"""
    return {**ELECTRICAL_ROUTES, **MECHANICAL_ROUTES}

def get_routing_mapping():
    """Retourne le mapping complet des routings"""
    return {**ELECTRICAL_ROUTINGS, **MECHANICAL_ROUTINGS}

def get_component_type_mapping():
    """Retourne le mapping des types de composants"""
    mapping = {}
    for domain, types in CUSTOM_COMPONENT_TYPES.items():
        mapping.update(types)
    return mapping

# Configuration par défaut pour les nouveaux projets
DEFAULT_PROJECT_CONFIG = {
    "project_name": "Nouveau Projet",
    "company": "Noovelia",
    "domain_prefix": "NOO",
    "auto_increment": True,
    "backup_frequency": "daily"
}

if __name__ == "__main__":
    print("Configuration du générateur de SKU")
    print("===================================")
    print(f"Domaines configurés: {list(DOMAINS.keys())}")
    print(f"Routes électriques: {len(ELECTRICAL_ROUTES)}")
    print(f"Routes mécaniques: {len(MECHANICAL_ROUTES)}")
    print(f"Format SKU: {SKU_FORMAT}")
    print("\\nConfiguration prête à l'utilisation ✅")
