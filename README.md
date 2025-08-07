# 🏭 Générateur de SKU Industriel - Noovelia

## 📋 Description

Application Python complète pour générer automatiquement des **codes SKU industriels** à partir de fichiers BOM (Bill of Materials) Excel. Le système utilise une **logique industrielle avancée** qui intègre les notions de **Route** et **Routing** pour optimiser la fabrication et la traçabilité.

## ✨ Fonctionnalités Principales

### 🔧 **Génération de SKU Intelligente**
- **Format Standardisé** : `DOMAINE-ROUTE-ROUTING-TYPE-SEQUENCE`
- **Logique Industrielle** : Intégration complète des processus de fabrication
- **Codes Français Lisibles** : Format hybride optimisé pour les opérateurs
- **Alphabet Industriel** : Évite les caractères ambigus (0/O, 1/I, 9/g)

### 📊 **Interface Utilisateur Intuitive**
- **Interface Graphique Modern** : Application tkinter avec design professionnel
- **Traitement en Temps Réel** : Barre de progression et feedback visuel
- **Recherche Avancée** : Retrouver n'importe quel composant par son SKU
- **Analyse Préalable** : Prévisualisation avant traitement complet

### 🎯 **Gestion des Données**
- **Base de Données SQLite** : Stockage local sécurisé et performant
- **Import Excel** : Support des formats .xlsx et .xls
- **Export Enrichi** : Fichiers Excel avec SKU et métadonnées
- **Historique Complet** : Traçabilité de tous les composants

## 🚀 Installation et Configuration

### Prérequis
- **Python 3.8+** (testé avec Python 3.13)
- **Système** : Windows, macOS, Linux

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/elboKazQC/SKU-Generetor.git
cd SKU-Generetor

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python gui.py
```

### Dépendances Principales
```txt
pandas>=2.0.0
openpyxl>=3.1.0
tkinter (inclus avec Python)
sqlite3 (inclus avec Python)
```

## 📖 Guide d'Utilisation

### 1. **Analyse d'un Nouveau BOM**

1. **Cliquez sur "📁 Analyser nouveau BOM"**
2. **Sélectionnez votre fichier Excel**
3. **Consultez le rapport d'analyse** :
   - Nombre de composants nouveaux vs existants
   - Répartition par domaine (ELEC/MECA)
   - Exemples de composants et SKU existants

### 2. **Traitement et Génération des SKU**

1. **Cliquez sur "⚙️ Traiter et générer SKU"**
2. **Sélectionnez le fichier BOM à traiter**
3. **Le système génère** :
   - Les SKU pour tous les nouveaux composants
   - Un fichier Excel enrichi avec les codes
   - La mise à jour de la base de données

### 3. **Recherche par SKU**

1. **Entrez un SKU** dans le champ de recherche
2. **Cliquez sur "🔍 Rechercher"** ou appuyez sur Entrée
3. **Consultez les informations** :
   - Détails du composant
   - Décodage complet du SKU
   - Composants similaires

## 🏷️ Format des SKU

### Structure Complète
```
MECA-ASS-ASM-PLIAGE-AAAA
 │    │   │    │      └─── Séquence unique (Base-29)
 │    │   │    └────────── Type français lisible étendu (5-6 lettres)
 │    │   └─────────────── Routing (opération)
 │    └─────────────────── Route (processus)
 └───────────────────────── Domaine (ELEC/MECA)
```

### Exemples Réels avec Codes Étendus
- **ELEC-CIR-IMP-CONNEC-AAAB** : Connecteur de circuit imprimé (à connecter)
- **MECA-ASS-MNT-PLIAGE-AAAC** : Pièce pliée pour assemblage (à plier)
- **ELEC-ALI-REG-RESIST-AAAD** : Résistance d'alimentation (à souder)
- **MECA-BOLT-BOLT-VISSER-AAAE** : Boulonnerie (à visser)

### Types Français Supportés (Codes Étendus 5-6 lettres)
| Code | Signification | Description | Action |
|------|---------------|-------------|---------|
| **PLIAGE** | Pièces Pliées | Composants formés par pliage | À plier |
| **USINER** | Pièces Usinées | Composants usinés/taillés | À usiner |
| **VISSER** | Boulonnerie | Vis, écrous, fixations | À visser |
| **CONNEC** | Connectique | Connecteurs électriques | À connecter |
| **MONTER** | Assemblage | Assemblage mécanique | À monter |
| **RESIST** | Résistances | Résistances électriques | À souder |
| **FUSIBL** | Fusibles | Protection fusible | À installer |
| **CIRCUI** | Circuits | Circuits intégrés | À implanter |

## 📁 Structure du Projet

```
SKU-Generetor/
├── 📄 gui.py                    # Interface utilisateur principale
├── 🔧 sku_generator.py          # Moteur de génération SKU
├── 📊 main.py                   # Processeur de fichiers BOM
├── 🔍 bom_analyzer.py           # Analyseur et comparateur
├── 💾 components.db             # Base de données SQLite
├── 📋 requirements.txt          # Dépendances Python
├── 📖 README.md                 # Cette documentation
└── 📁 SKU_*.xlsx               # Fichiers de sortie générés
```

## ⚙️ Configuration Avancée

### Personnalisation des Types
Modifiez le fichier `sku_generator.py` pour ajouter de nouveaux types :

```python
type_mapping = {
    "Pièces Pliées": "PLIE",
    "Pièces Usinées": "USIN", 
    "Votre Nouveau Type": "NOUV",
    # Ajoutez vos types personnalisés
}
```

### Domaines Supportés
- **ELEC** : Composants électriques/électroniques
- **MECA** : Composants mécaniques/structurels

### Format Excel d'Entrée
Votre fichier BOM doit contenir ces colonnes :
- **Name** : Nom du composant
- **Description** : Description détaillée
- **Domain** : ELEC ou MECA
- **Route** : Processus de fabrication
- **Routing** : Opération spécifique
- **Component Type** : Type de composant

## 🔧 Fonctionnalités Techniques

### Base de Données
- **SQLite embarqué** : Pas de serveur requis
- **Schema optimisé** : Index pour recherches rapides
- **Sauvegarde automatique** : Aucune perte de données

### Algorithme de Génération
1. **Normalisation** : Suppression des accents et caractères spéciaux
2. **Alphabet Industriel** : 29 caractères sans ambiguïté
3. **Séquence Base-29** : Codage compact et lisible
4. **Vérification d'unicité** : Garantie d'unicité des SKU

### Gestion des Erreurs
- **Validation d'accès fichier** : Détection OneDrive/permissions
- **Formats Excel flexibles** : Support multi-onglets
- **Récupération d'erreurs** : Messages explicites pour l'utilisateur

## 📊 Statistiques et Monitoring

### Tableau de Bord Intégré
- **Composants totaux** en base
- **Répartition par domaine** (ELEC/MECA)
- **Historique des traitements**
- **Derniers ajouts**

### Rapports Détaillés
- **Analyse comparative** nouveau vs existant
- **Exemples de SKU générés**
- **Composants similaires**
- **Statistiques de traitement**

## 🛠️ Maintenance et Support

### Nettoyage de Base
```bash
# Supprimer tous les composants (attention : irréversible)
python -c "
from sku_generator import SKUGenerator
import sqlite3
conn = sqlite3.connect('components.db')
conn.execute('DELETE FROM components')
conn.commit()
conn.close()
print('Base de données nettoyée')
"
```

### Sauvegarde
```bash
# Créer une sauvegarde de la base
copy components.db components_backup_$(date +%Y%m%d).db
```

## 🎯 Cas d'Usage

### 1. **Nouveau Projet**
- Analysez d'abord votre BOM
- Vérifiez les classifications
- Traitez et générez les SKU
- Intégrez dans votre ERP

### 2. **Mise à Jour BOM**
- L'analyse différentielle montre les nouveautés
- Seuls les nouveaux composants reçoivent un SKU
- Maintien de la cohérence historique

### 3. **Recherche et Traçabilité**
- Retrouvez instantanément un composant
- Visualisez la structure du SKU
- Identifiez les composants similaires

## 📞 Contact et Support

**Développé pour Noovelia**
- 🏢 **Entreprise** : Noovelia
- 👨‍💻 **Développeur** : Équipe Technique Noovelia
- 📧 **Support** : [Votre email de support]
- 🐛 **Issues** : GitHub Issues du repository

## 📝 Licence

Ce projet est développé spécifiquement pour Noovelia. Tous droits réservés.

---

## 🔄 Historique des Versions

### v2.2 - Codes Étendus Ultra-Lisibles (Actuel)
- ✅ Codes français 5-6 lettres (PLIAGE, USINER, VISSER, etc.)
- ✅ Instructions d'action intégrées dans le SKU
- ✅ Compréhension immédiate pour les opérateurs
- ✅ Réduction des erreurs de manipulation

### v2.1 - Format Hybride Français
- ✅ Codes français lisibles (PLIE, USIN, BOUL, etc.)
- ✅ Interface utilisateur améliorée
- ✅ Recherche avancée avec décodage
- ✅ Alphabet industriel optimisé

### v2.0 - Interface Graphique
- ✅ Interface tkinter complète
- ✅ Analyse préalable des BOM
- ✅ Gestion des erreurs OneDrive
- ✅ Statistiques en temps réel

### v1.0 - Version Initiale
- ✅ Génération SKU basique
- ✅ Import/Export Excel
- ✅ Base de données SQLite

---

*Générateur de SKU Industriel - Optimisé pour la production manufacturière moderne* 🏭

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
