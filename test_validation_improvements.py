#!/usr/bin/env python3
"""
Test des améliorations de la fenêtre de validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from component_validation_window import ComponentValidationWindow
from sku_generator import Component
import tkinter as tk

def test_validation_improvements():
    """Test les améliorations de validation"""
    
    print("🧪 TEST DES AMÉLIORATIONS DE VALIDATION")
    print("=" * 50)
    
    # Créer des composants de test
    test_components = {
        "ELEC": [
            Component(
                name="Résistance Test",
                description="Résistance 100Ω pour test",
                domain="ELEC",
                component_type="RESIST",
                route="",
                routing="",
                manufacturer="TestCorp",
                manufacturer_part="R100",
                quantity=10,
                designator="R1"
            ),
            Component(
                name="Condensateur Test",
                description="Condensateur 10µF pour test",
                domain="ELEC",
                component_type="CONDEN",
                route="",
                routing="",
                manufacturer="TestCorp",
                manufacturer_part="C10",
                quantity=5,
                designator="C1"
            )
        ],
        "MECA": [
            Component(
                name="Vis Test",
                description="Vis M6x20 pour test",
                domain="MECA",
                component_type="VIS",
                route="",
                routing="",
                manufacturer="TestCorp",
                manufacturer_part="V620",
                quantity=20
            )
        ]
    }
    
    print("✅ Composants de test créés:")
    for domain, components in test_components.items():
        print(f"  - {domain}: {len(components)} composants")
    
    print("\n🚀 Lancement de la fenêtre de validation...")
    print("📋 Fonctionnalités à tester:")
    print("  1. ✅ Clic individuel pour sélectionner/désélectionner")
    print("  2. 📋 Aperçu des SKU en temps réel")
    print("  3. 🔄 Boutons de sélection globale")
    print("  4. 📊 Statistiques en temps réel")
    print("  5. 🖼️ Interface avec panneau divisé")
    
    # Créer la fenêtre principale
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    
    def on_validation_complete(selected_components):
        """Callback de test"""
        print("\n✅ VALIDATION TERMINÉE !")
        total = sum(len(components) for components in selected_components.values())
        print(f"📊 Composants sélectionnés: {total}")
        
        for domain, components in selected_components.items():
            print(f"  - {domain}: {len(components)} composants")
        
        root.quit()
    
    # Créer la fenêtre de validation
    validation_window = ComponentValidationWindow(
        root, 
        test_components, 
        "fichier_test.xlsx", 
        callback=on_validation_complete
    )
    
    print("\n🎯 INSTRUCTIONS DE TEST:")
    print("1. Cliquez sur les lignes pour sélectionner/désélectionner")
    print("2. Vérifiez l'aperçu des SKU dans le panneau de droite")
    print("3. Testez les boutons 'Tout sélectionner' et 'Tout désélectionner'")
    print("4. Vérifiez les statistiques en temps réel")
    print("5. Cliquez sur 'Générer les SKU' ou 'Annuler' pour fermer")
    
    # Lancer la boucle d'événements
    root.mainloop()
    
    print("\n🎉 Test terminé!")

if __name__ == "__main__":
    test_validation_improvements()
