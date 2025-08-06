# Générateur de SKU Industriel avec Logique de Route et Routing

## Vue d'ensemble
Ce système génère automatiquement des SKU (Stock Keeping Units) pour les composants électriques et mécaniques à partir de fichiers BOM Excel, en incluant la logique de route et routing industriel.

## Structure des SKU Générés

### Format : `[DOMAINE]-[ROUTE]-[ROUTING]-[TYPE]-[SEQUENCE]`

**Exemples :**
- `ELEC-TERM-STD-CCSS-00001` (Électrique/Terminal/Standard/Cosses)
- `MECA-BOLT-BOLT-015B-00001` (Mécanique/Boulonnerie/Bolt/015)
- `ELEC-ASS-ASM-SSMB-00001` (Électrique/Assemblage/Assembly/Assemblage)
- `MECA-LASER-CUT-111P-00001` (Mécanique/Laser/Cut/Pièces découpées)

## Fonctionnalités

### ✅ Lecture BOM Excel
- Support des feuilles multiples (BOM Électrique, BOM Mécanique)
- Détection automatique des colonnes
- Validation des données

### ✅ Génération SKU Intelligente
- **Routes** : ASS (Assemblage), CONN (Connecteur), TERM (Terminal), BOLT (Boulonnerie), LASER (Découpe laser), etc.
- **Routings** : ASM (Assembly), WIRE (Filage), BEND (Pliage), CUT (Découpe), MILL (Usinage), etc.
- **Types** : Basés sur les composants (CCSS=Cosses, BOLT=Boulons, etc.)
- **Séquences** : Numérotation automatique avec padding

### ✅ Détection des Doublons
- Hash MD5 des composants pour identifier les pièces similaires
- Réutilisation des SKU existants
- Évite la duplication

### ✅ Base de Données Persistante
- SQLite pour stocker les composants et SKU
- Historique complet
- Compteurs par catégorie

### ✅ Interface Utilisateur
- Interface graphique simple
- Analyse des BOM avant traitement
- Export Excel des résultats

## Installation

### Prérequis
- Python 3.8+
- Modules requis dans `requirements.txt`

### Installation rapide
```bash
# Cloner le projet
git clone <repository-url>
cd SKU-Generetor

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement (Windows)
.venv\\Scripts\\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### 1. Interface Graphique (Recommandé)
```bash
python gui.py
```

### 2. Ligne de Commande
```bash
# Traitement direct
python main.py

# Analyse seulement
python bom_analyzer.py
```

### 3. Module Python
```python
from sku_generator import SKUGenerator, Component

# Initialiser
generator = SKUGenerator()

# Créer un composant
component = Component(
    name="Vis M6x20",
    description="Vis à tête hexagonale",
    domain="MECA",
    component_type="015 | BOULONNERIE",
    route="",
    routing=""
)

# Générer SKU
sku = generator.generate_sku(component)
print(f"SKU généré: {sku}")
```

## Structure des Fichiers

```
SKU-Generetor/
├── sku_generator.py      # Classe principale génération SKU
├── main.py              # Script traitement BOM
├── bom_analyzer.py      # Analyse et comparaison BOM
├── gui.py               # Interface graphique
├── requirements.txt     # Dépendances Python
├── README.md           # Cette documentation
├── sku_database.db     # Base de données SQLite (créée automatiquement)
└── (V2.1) BOM unifié électrique-mécanique.xlsx  # Fichier BOM exemple
```

## Configuration

### Mapping des Routes et Routings

Le système utilise des mappings configurables dans `sku_generator.py` :

```python
# Routes électriques
route_mapping = {
    "Assemblage": "ASS",
    "Connecteurs": "CONN",
    "Borniers": "TERM",
    "Communication": "COMM",
    "Alimentation": "POWER",
    # ...
}

# Routings mécaniques
routing_mapping = {
    "BOULONNERIE": "BOLT",
    "PIÈCES PLIÉES": "BEND",
    "PIÈCES USINÉES": "MILL",
    "PIÈCES DÉCOUPÉES LASER": "CUT",
    # ...
}
```

### Format de Fichier BOM Supporté

**Feuille "BOM Électrique" :**
- `Name` : Nom du composant
- `Description` : Description
- `ComponentType` : Type de composant
- `Manufacturer` : Fabricant
- `Manufacturer PN` : Numéro de pièce fabricant
- `Quantity` : Quantité
- `Designator` : Désignateur

**Feuille "BOM Mécanique" :**
- `Type` : Type de composant
- `No. de pièce` : Numéro de pièce
- `Description Française` : Description
- `Manufacturier` : Fabricant
- `QTE TOTALE` : Quantité totale

## Exemples de Résultats

### Statistiques obtenues sur le BOM test :
- **Total** : 455 composants traités
- **Électrique** : 177 composants
- **Mécanique** : 278 composants

### Exemples de SKU générés :

**Domaine Électrique :**
- Terminals : `ELEC-TERM-STD-CCSS-00001` à `ELEC-TERM-STD-CCSS-00022`
- Assemblages : `ELEC-ASS-ASM-SSMB-00001` à `ELEC-ASS-ASM-SSMB-00022`
- Connecteurs : `ELEC-CONN-STD-CNNC-00001` à `ELEC-CONN-STD-CNNC-00006`

**Domaine Mécanique :**
- Boulonnerie : `MECA-BOLT-BOLT-015B-00001` à `MECA-BOLT-BOLT-015B-00071`
- Pièces pliées : `MECA-BEND-BEND-121P-00001` à `MECA-BEND-BEND-121P-00048`
- Découpe laser : `MECA-LASER-CUT-111P-00001` à `MECA-LASER-CUT-111P-00023`

## Avantages du Système

### 🎯 Logique Industrielle
- **Routes** intégrées dans le SKU pour identifier le processus de fabrication
- **Routings** pour définir les étapes de transformation
- Facilite la **planification de production**

### 🔄 Gestion des Doublons
- Détection automatique des composants similaires
- Réutilisation des SKU existants
- Évite la prolifération de références

### 📊 Traçabilité Complète
- Historique complet en base de données
- Suivi des créations et modifications
- Statistiques par domaine/route/routing

### 🚀 Performance
- Traitement rapide de gros volumes
- Base de données optimisée
- Interface responsive

### 🔧 Flexibilité
- Mappings configurables
- Support de différents formats BOM
- Extensible pour nouveaux domaines

## Support et Contact

Pour toute question ou assistance :
- 📧 Email : [votre-email]
- 📁 Issues GitHub : [repository-url]/issues
- 📖 Documentation : Ce fichier README.md

## Licence

Développé pour Noovelia - Usage interne.

---
*Générateur de SKU Industriel v1.0 - Développé avec GitHub Copilot*
