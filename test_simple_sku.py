#!/usr/bin/env python3
"""
Test simple du nouveau format SKU simplifié
"""

from sku_generator import SKUGenerator, Component

# Test rapide
generator = SKUGenerator("test_simple.db")

# Composant test
component = Component(
    name="Vis M6",
    description="Vis hexagonale",
    domain="MECA",
    component_type="BOULONNERIE",
    route="",
    routing=""
)

print("Test génération SKU simplifié...")
try:
    sku = generator.generate_sku(component)
    print(f"SKU généré: {sku}")

    # Test décodage
    decoded = generator.decode_sku_parts(sku)
    print(f"Décodage: {decoded}")

    print("✅ Test réussi!")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
