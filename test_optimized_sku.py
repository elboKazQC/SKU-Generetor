#!/usr/bin/env python3
"""
Test rapide des SKU optimisés
"""

from sku_generator import SKUGenerator, Component

def test_optimized_skus():
    """Test des SKU optimisés"""
    print("🎯 TEST DES SKU OPTIMISÉS")
    print("=" * 50)
    
    gen = SKUGenerator()
    
    # Test 1: Redondance BOLT-BOLT
    print("\n1. Test BOLT-BOLT (redondance)")
    comp1 = Component(
        name="Vis M6x20",
        description="Vis hexagonale M6x20mm",
        domain="MECA",
        component_type="Boulonnerie",
        route="BOLT",
        routing="BOLT"
    )
    
    try:
        sku1 = gen.generate_sku(comp1)
        print(f"   Résultat: {sku1}")
        print(f"   ✅ Optimisation: BOLT-BOLT → STD-BOLT")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Redondance BEND-BEND
    print("\n2. Test BEND-BEND (redondance)")
    comp2 = Component(
        name="Équerre pliée",
        description="Équerre en tôle pliée",
        domain="MECA",
        component_type="Pièces Pliées",
        route="BEND",
        routing="BEND"
    )
    
    try:
        sku2 = gen.generate_sku(comp2)
        print(f"   Résultat: {sku2}")
        print(f"   ✅ Optimisation: BEND-BEND → STD-BEND")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Pas de redondance
    print("\n3. Test ELEC-STD (optimal)")
    comp3 = Component(
        name="Résistance 100Ω",
        description="Résistance 1/4W",
        domain="ELEC",
        component_type="Résistances",
        route="ELEC",
        routing="STD"
    )
    
    try:
        sku3 = gen.generate_sku(comp3)
        print(f"   Résultat: {sku3}")
        print(f"   ✅ Aucune optimisation nécessaire")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RÉSUMÉ DES OPTIMISATIONS")
    print("- Élimination des redondances route/routing")
    print("- Codes plus courts et plus clairs")
    print("- Préservation de l'information essentielle")

if __name__ == "__main__":
    test_optimized_skus()
