#!/usr/bin/env python3
"""
Test des améliorations SKU industrielles
"""

from sku_generator import SKUGenerator, Component

def test_industrial_sku():
    gen = SKUGenerator()
    
    print("🔤 ALPHABET SKU INDUSTRIEL")
    print("=" * 50)
    print(f"Alphabet: {gen.sku_alphabet}")
    print(f"Longueur: {len(gen.sku_alphabet)} caractères")
    print("Caractères supprimés: I, L, O, U, V, 0, 1, 9")
    
    print("\n🔧 TESTS DE NORMALISATION")
    print("=" * 50)
    test_cases = [
        "Pièces Pliées",
        "Résistance 1kΩ", 
        "Léo & Voilà",
        "I/O Module",
        "Circuit Intégré",
        "Boulonnerie Ø10",
        "Plaque Aluminium"
    ]
    
    for text in test_cases:
        normalized = gen.normalize_text(text, 4)
        print(f"'{text:<20}' → '{normalized}'")
    
    print("\n📊 TESTS DE SÉQUENCES")
    print("=" * 50)
    for i in range(1, 11):
        seq = gen.format_sequence(i)
        print(f"Séquence {i:2d} → {seq}")
    
    print("\n🆕 EXEMPLE DE SKU GÉNÉRÉ")
    print("=" * 50)
    
    # Test avec un composant
    comp = Component(
        name="Plaque de support",
        description="Plaque en aluminium pliée",
        domain="MECA",
        component_type="PIÈCES PLIÉES",
        route="BEND",
        routing="BEND"
    )
    
    sku = gen.generate_sku(comp)
    print(f"Composant: {comp.name}")
    print(f"SKU généré: {sku}")
    
    print("\n✅ TESTS TERMINÉS")

if __name__ == "__main__":
    test_industrial_sku()
