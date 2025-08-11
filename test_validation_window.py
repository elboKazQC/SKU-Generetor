#!/usr/bin/env python3
"""
Test de la fenêtre de validation des composants
"""

import tkinter as tk
from sku_generator import Component
from component_validation_window import ComponentValidationWindow

def test_validation_window():
    """Tester la fenêtre de validation avec des données simulées"""

    # Créer des composants de test
    electrical_components = [
        Component(
            name="Résistance 100Ω",
            description="Résistance 1/4W 5%",
            domain="ELEC",
            component_type="Résistances",
            route="",
            routing="",
            manufacturer="Vishay",
            manufacturer_part="RN55C1000B",
            quantity=10,
            designator="R1,R2,R3"
        ),
        Component(
            name="Condensateur 10µF",
            description="Condensateur électrolytique",
            domain="ELEC",
            component_type="Condensateurs",
            route="",
            routing="",
            manufacturer="Panasonic",
            manufacturer_part="ECA-1HM100",
            quantity=5,
            designator="C1,C2"
        ),
        Component(
            name="Connecteur USB-C",
            description="Connecteur USB Type-C",
            domain="ELEC",
            component_type="Connecteurs",
            route="",
            routing="",
            manufacturer="Amphenol",
            manufacturer_part="12401832E4#2A",
            quantity=1,
            designator="J1"
        )
    ]

    mechanical_components = [
        Component(
            name="Vis M4x16",
            description="Vis à tête hexagonale M4x16mm",
            domain="MECA",
            component_type="015 | BOULONNERIE",
            route="",
            routing="",
            manufacturer="Würth",
            manufacturer_part="912004160",
            quantity=8
        ),
        Component(
            name="Plaque support",
            description="Plaque support en aluminium",
            domain="MECA",
            component_type="121 | PIÈCES PLIÉES",
            route="",
            routing="",
            manufacturer="Local",
            manufacturer_part="PLQ-001",
            quantity=1
        ),
        Component(
            name="Boîtier plastique",
            description="Boîtier en ABS noir",
            domain="MECA",
            component_type="PLASTIQUE",
            route="",
            routing="",
            manufacturer="Hammond",
            manufacturer_part="1593HAA",
            quantity=1
        )
    ]

    # Données de test
    components_data = {
        "ELEC": electrical_components,
        "MECA": mechanical_components
    }

    def on_validation_complete(selected_components):
        """Callback appelé après validation"""
        print("🎯 COMPOSANTS SÉLECTIONNÉS:")
        for domain, components in selected_components.items():
            print(f"\\n{domain}: {len(components)} composants")
            for comp in components:
                print(f"  - {comp.name}")

        # Fermer l'application après validation
        root.destroy()

    # Créer la fenêtre principale
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale

    # Créer la fenêtre de validation
    validation_window = ComponentValidationWindow(
        root,
        components_data,
        "test_bom.xlsx",
        callback=on_validation_complete
    )

    print("🧪 FENÊTRE DE VALIDATION OUVERTE")
    print("Sélectionnez/désélectionnez les composants et cliquez sur 'Générer les SKU'")

    root.mainloop()

if __name__ == "__main__":
    test_validation_window()
