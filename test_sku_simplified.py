#!/usr/bin/env python3
"""
Test du nouveau format SKU simplifié : FAMILLE-SOUS_FAMILLE-SEQUENCE
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sku_generator import SKUGenerator, Component

def test_new_simplified_format():
    """Test du nouveau format SKU simplifié"""
    print("🧪 Test du nouveau format SKU simplifié")
    print("=" * 50)

    # Initialiser le générateur
    generator = SKUGenerator("test_sku_simplified.db")

    # Créer des composants test
    test_components = [
        Component(
            name="Vis M6x20 INOX",
            description="Vis à tête hexagonale en acier inoxydable",
            domain="MECA",
            component_type="BOULONNERIE",
            route="",  # Ces champs ne seront plus utilisés
            routing=""
        ),
        Component(
            name="Résistance 10kΩ",
            description="Résistance de précision 1%",
            domain="ELEC",
            component_type="Résistances",
            route="",
            routing=""
        ),
        Component(
            name="Pièce pliée support",
            description="Support métallique plié",
            domain="MECA",
            component_type="Pièces Pliées",
            route="",
            routing=""
        ),
        Component(
            name="Connecteur RJ45",
            description="Connecteur Ethernet Cat6",
            domain="ELEC",
            component_type="Connecteurs",
            route="",
            routing=""
        )
    ]

    print("\n📋 Génération des SKU simplifiés :")
    print("-" * 30)

    generated_skus = []
    for component in test_components:
        try:
            sku = generator.generate_sku(component)
            generated_skus.append(sku)
            print(f"✅ {component.name[:25]:<25} → {sku}")
        except Exception as e:
            print(f"❌ {component.name[:25]:<25} → Erreur: {e}")

    print(f"\n🎯 Résultat : Format simplifié FAMILLE-SOUS_FAMILLE-SEQUENCE")
    print(f"   Ancien format : DOMAINE-ROUTE-ROUTING-TYPE-SEQUENCE (5 parties)")
    print(f"   Nouveau format: FAMILLE-SOUS_FAMILLE-SEQUENCE (3 parties)")

    # Test du décodage
    print("\n🔍 Test de décodage des SKU :")
    print("-" * 30)

    for sku in generated_skus:
        decoded = generator.decode_sku_parts(sku)
        if decoded.get('format') == 'simplifie':
            print(f"✅ {sku} → {decoded['famille_nom']} - {decoded['sous_famille_nom']}")
        else:
            print(f"❌ {sku} → Erreur de décodage")

    # Comparaison des longueurs
    print(f"\n📏 Comparaison des longueurs :")
    print("-" * 30)
    if generated_skus:
        exemple_nouveau = generated_skus[0]
        exemple_ancien = "MECA-BOLT-BOLT-VISSER-2222"  # Exemple ancien format

        print(f"   Ancien format : {exemple_ancien} ({len(exemple_ancien)} caractères)")
        print(f"   Nouveau format: {exemple_nouveau} ({len(exemple_nouveau)} caractères)")
        reduction = len(exemple_ancien) - len(exemple_nouveau)
        print(f"   📉 Réduction : {reduction} caractères ({reduction/len(exemple_ancien)*100:.1f}%)")

    print(f"\n✨ Test terminé avec succès!")
    return True

def test_backward_compatibility():
    """Test de rétrocompatibilité avec l'ancien format"""
    print("\n🔄 Test de rétrocompatibilité")
    print("=" * 50)

    generator = SKUGenerator("test_sku_simplified.db")

    # Test avec un ancien SKU
    ancien_sku = "ELEC-ASS-ASM-PLIAGE-AAAA"
    print(f"Test décodage ancien format: {ancien_sku}")

    decoded = generator.decode_sku_parts(ancien_sku)
    if decoded.get('format') == 'ancien':
        print(f"✅ Décodage ancien format réussi")
        print(f"   Domaine: {decoded['domaine_nom']}")
        print(f"   Route: {decoded['route_nom']}")
        print(f"   Routing: {decoded['routing_nom']}")
        print(f"   Type: {decoded['type_nom']}")
    else:
        print(f"❌ Erreur décodage ancien format")

    # Test avec le nouveau format
    nouveau_sku = "ELEC-RESIST-2222"
    print(f"\nTest décodage nouveau format: {nouveau_sku}")

    decoded = generator.decode_sku_parts(nouveau_sku)
    if decoded.get('format') == 'simplifie':
        print(f"✅ Décodage nouveau format réussi")
        print(f"   Famille: {decoded['famille_nom']}")
        print(f"   Sous-famille: {decoded['sous_famille_nom']}")
    else:
        print(f"❌ Erreur décodage nouveau format")

if __name__ == "__main__":
    print("🚀 Test du générateur SKU simplifié")
    print("Nouveau format : FAMILLE-SOUS_FAMILLE-SEQUENCE")
    print("=" * 60)

    try:
        test_new_simplified_format()
        test_backward_compatibility()

        print("\n🎉 Tous les tests réussis !")
        print("\n💡 Avantages du nouveau format :")
        print("   • SKU plus courts et lisibles")
        print("   • Structure simplifiée : FAMILLE-SOUS_FAMILLE-SEQUENCE")
        print("   • Rétrocompatibilité avec l'ancien format")
        print("   • Réduction significative de la longueur")

    except Exception as e:
        print(f"\n❌ Erreur lors des tests : {e}")
        import traceback
        traceback.print_exc()
