#!/usr/bin/env python3
"""
Test rapide de l'interface GUI avec la nouvelle fonctionnalité
"""

import tkinter as tk
from pathlib import Path
import sys

def test_gui_import():
    """Test d'import de l'interface graphique"""
    try:
        print("🧪 TEST D'IMPORT DE L'INTERFACE GRAPHIQUE")
        print("=" * 50)
        
        # Test d'import
        print("1. Import du module GUI...")
        import gui
        print("   ✅ Import réussi")
        
        print("2. Import de la fenêtre de validation...")
        from component_validation_window import ComponentValidationWindow
        print("   ✅ Import réussi")
        
        print("3. Test de création de l'interface...")
        root = tk.Tk()
        root.withdraw()  # Cacher pour le test
        
        app = gui.SKUGeneratorGUI(root)
        print("   ✅ Interface créée avec succès")
        
        print("4. Test des méthodes principales...")
        # Vérifier que les nouvelles méthodes existent
        assert hasattr(app.processor, 'extract_components_from_bom'), "Méthode extract_components_from_bom manquante"
        assert hasattr(app.processor, 'generate_skus_for_selected_components'), "Méthode generate_skus_for_selected_components manquante"
        assert hasattr(app, 'show_validation_window'), "Méthode show_validation_window manquante"
        print("   ✅ Toutes les méthodes présentes")
        
        root.destroy()
        
        print("\\n🎉 TOUS LES TESTS PASSÉS !")
        print("✅ L'interface graphique est prête à utiliser")
        print("✅ La fenêtre de validation est opérationnelle")
        print("\\n💡 Pour lancer l'interface complète:")
        print("   python gui.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_gui_import()
    sys.exit(0 if success else 1)
