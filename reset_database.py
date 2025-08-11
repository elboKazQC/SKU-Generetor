#!/usr/bin/env python3
"""
Script pour réinitialiser complètement la base de données SKU
"""

import sqlite3
import os
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def reset_database(db_path: str = "sku_database.db"):
    """Réinitialise complètement la base de données"""
    
    print("🗑️ RÉINITIALISATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    # Vérifier si la base existe
    if Path(db_path).exists():
        print(f"📁 Base de données trouvée: {db_path}")
        
        # Afficher les statistiques avant suppression
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Compter les composants
            cursor.execute("SELECT COUNT(*) FROM components")
            component_count = cursor.fetchone()[0]
            
            # Compter les compteurs
            cursor.execute("SELECT COUNT(*) FROM sku_counters")
            counter_count = cursor.fetchone()[0]
            
            # Statistiques par domaine
            cursor.execute("SELECT domain, COUNT(*) FROM components GROUP BY domain")
            domain_stats = cursor.fetchall()
            
            conn.close()
            
            print(f"📊 Statistiques actuelles:")
            print(f"  - Total composants: {component_count}")
            print(f"  - Compteurs SKU: {counter_count}")
            for domain, count in domain_stats:
                print(f"  - {domain}: {count} composants")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture des statistiques: {e}")
        
        # Supprimer la base de données
        try:
            os.remove(db_path)
            print(f"✅ Base de données supprimée: {db_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    else:
        print(f"ℹ️ Aucune base de données trouvée: {db_path}")
    
    # Créer une nouvelle base vide
    try:
        from sku_generator import SKUGenerator
        
        print(f"🔄 Création d'une nouvelle base de données...")
        generator = SKUGenerator(db_path)
        
        # Vérifier que les tables sont créées
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Nouvelle base de données créée avec {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la nouvelle base: {e}")
        return False

def confirm_reset():
    """Demande confirmation avant réinitialisation"""
    print("⚠️ ATTENTION: Cette opération va supprimer TOUS les SKU existants!")
    print("Cette action est IRRÉVERSIBLE.")
    print()
    
    while True:
        response = input("Voulez-vous vraiment réinitialiser la base de données? (oui/non): ").lower().strip()
        
        if response in ['oui', 'o', 'yes', 'y']:
            return True
        elif response in ['non', 'n', 'no']:
            return False
        else:
            print("Veuillez répondre par 'oui' ou 'non'")

def main():
    """Fonction principale"""
    print("🔄 OUTIL DE RÉINITIALISATION DE LA BASE DE DONNÉES SKU")
    print("=" * 60)
    print()
    
    # Demander confirmation
    if not confirm_reset():
        print("❌ Opération annulée par l'utilisateur")
        return
    
    print()
    
    # Réinitialiser la base
    success = reset_database()
    
    print()
    if success:
        print("🎉 RÉINITIALISATION TERMINÉE AVEC SUCCÈS!")
        print("✅ La base de données est maintenant vide et prête à utiliser")
        print("💡 Vous pouvez maintenant traiter de nouveaux fichiers BOM")
    else:
        print("❌ ÉCHEC DE LA RÉINITIALISATION")
        print("🔧 Vérifiez les permissions et réessayez")

if __name__ == "__main__":
    main()
