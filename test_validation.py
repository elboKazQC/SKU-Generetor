#!/usr/bin/env python3
"""
Test de validation des composants pour éviter la création de SKU vides
"""

from sku_generator import SKUGenerator, Component
import logging

# Configuration du logging pour voir les messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_component_validation():
    """Test de la validation des composants"""
    print("🧪 TEST DE VALIDATION DES COMPOSANTS")
    print("=" * 50)
    
    generator = SKUGenerator()
    
    # Test 1: Composant valide
    print("\n1. ✅ Test composant valide")
    valid_component = Component(
        name="Résistance 100Ω",
        description="Résistance 1/4W 5%",
        domain="ELEC",
        component_type="Résistances",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(valid_component)
        print(f"   SKU généré: {sku}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Nom vide
    print("\n2. ❌ Test nom vide")
    empty_name_component = Component(
        name="",
        description="Description valide",
        domain="ELEC",
        component_type="Résistances",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(empty_name_component)
        print(f"   ⚠️ SKU créé malgré nom vide: {sku}")
    except ValueError as e:
        print(f"   ✅ Composant rejeté correctement: {e}")
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
    
    # Test 3: Nom invalide (nan)
    print("\n3. ❌ Test nom 'nan'")
    nan_component = Component(
        name="nan",
        description="Description valide",
        domain="ELEC",
        component_type="Résistances",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(nan_component)
        print(f"   ⚠️ SKU créé malgré nom 'nan': {sku}")
    except ValueError as e:
        print(f"   ✅ Composant rejeté correctement: {e}")
    
    # Test 4: Domaine invalide
    print("\n4. ❌ Test domaine invalide")
    invalid_domain_component = Component(
        name="Vis M6",
        description="Vis hexagonale",
        domain="INVALID",
        component_type="Boulonnerie",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(invalid_domain_component)
        print(f"   ⚠️ SKU créé malgré domaine invalide: {sku}")
    except ValueError as e:
        print(f"   ✅ Composant rejeté correctement: {e}")
    
    # Test 5: Type de composant vide
    print("\n5. ❌ Test type composant vide")
    empty_type_component = Component(
        name="Composant mystère",
        description="Description valide",
        domain="ELEC",
        component_type="",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(empty_type_component)
        print(f"   ⚠️ SKU créé malgré type vide: {sku}")
    except ValueError as e:
        print(f"   ✅ Composant rejeté correctement: {e}")
    
    # Test 6: Description vide (doit être accepté mais remplacé)
    print("\n6. ⚠️ Test description vide (doit être accepté)")
    empty_desc_component = Component(
        name="Composant sans description",
        description="",
        domain="MECA",
        component_type="Boulonnerie",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(empty_desc_component)
        print(f"   ✅ SKU généré avec description par défaut: {sku}")
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
    
    # Test 7: Espaces uniquement dans le nom
    print("\n7. ❌ Test nom avec espaces uniquement")
    spaces_component = Component(
        name="   ",
        description="Description valide",
        domain="ELEC",
        component_type="Condensateurs",
        route="",
        routing=""
    )
    
    try:
        sku = generator.generate_sku(spaces_component)
        print(f"   ⚠️ SKU créé malgré nom avec espaces: {sku}")
    except ValueError as e:
        print(f"   ✅ Composant rejeté correctement: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TEST TERMINÉ")
    print("✅ Les composants invalides doivent être rejetés")
    print("⚠️ Les composants valides doivent générer un SKU")

if __name__ == "__main__":
    test_component_validation()
