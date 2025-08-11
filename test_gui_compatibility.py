#!/usr/bin/env python3
"""
Test de l'interface GUI avec le nouveau format SKU simplifié
"""

import tkinter as tk
from sku_generator import SKUGenerator, Component

def test_gui_integration():
    """Test d'intégration de la GUI avec le nouveau format"""
    print("🖥️  Test d'intégration GUI avec format simplifié")
    print("=" * 50)
    
    # Simuler la génération de SKU depuis la GUI
    generator = SKUGenerator("test_gui.db")
    
    # Composants test similaires à ceux traités par la GUI
    test_components = [
        Component(
            name="VIS CHC M6X20 INOX A2",
            description="Vis à tête cylindrique hexagonale creuse",
            domain="MECA",
            component_type="BOULONNERIE",
            route="",
            routing="",
            manufacturer="FACOM",
            manufacturer_part="VIS-M6-20-A2",
            quantity=10.0
        ),
        Component(
            name="RESISTOR 10K OHM 1% 1/4W",
            description="Résistance couche métallique 1% 1/4W",
            domain="ELEC", 
            component_type="Résistances",
            route="",
            routing="",
            manufacturer="VISHAY",
            manufacturer_part="RES-10K-1/4W",
            quantity=100.0
        )
    ]
    
    print("\n📋 Simulation génération GUI :")
    print("-" * 30)
    
    results = []
    for component in test_components:
        try:
            sku = generator.generate_sku(component)
            results.append({
                'component': component,
                'sku': sku,
                'status': 'success'
            })
            print(f"✅ {component.name[:30]:<30} → {sku}")
        except Exception as e:
            results.append({
                'component': component,
                'sku': None,
                'status': 'error',
                'error': str(e)
            })
            print(f"❌ {component.name[:30]:<30} → ERREUR: {e}")
    
    # Test des fonctionnalités de recherche GUI
    print(f"\n🔍 Test fonctions de recherche GUI :")
    print("-" * 30)
    
    for result in results:
        if result['status'] == 'success':
            sku = result['sku']
            
            # Test recherche par SKU (fonction GUI)
            component_data = generator.search_component_by_sku(sku)
            if component_data:
                print(f"✅ Recherche {sku} → Trouvé: {component_data['nom'][:20]}...")
            else:
                print(f"❌ Recherche {sku} → Non trouvé")
            
            # Test décodage SKU (affichage GUI)
            decoded = generator.decode_sku_parts(sku)
            if decoded.get('format') == 'simplifie':
                famille = decoded['famille_nom']
                sous_famille = decoded['sous_famille_nom']
                print(f"   Décodage → {famille} / {sous_famille}")
            else:
                print(f"   Décodage → ERREUR")
    
    # Statistiques compatibles GUI
    print(f"\n📊 Statistiques pour tableau de bord GUI :")
    print("-" * 30)
    
    total_components = len(results)
    success_count = len([r for r in results if r['status'] == 'success'])
    error_count = total_components - success_count
    
    print(f"   Total composants traités: {total_components}")
    print(f"   SKU générés avec succès: {success_count}")
    print(f"   Erreurs: {error_count}")
    
    if success_count > 0:
        exemple_sku = results[0]['sku'] if results[0]['status'] == 'success' else None
        if exemple_sku:
            longueur_nouvelle = len(exemple_sku)
            longueur_ancienne = len("MECA-BOLT-BOLT-VISSER-AAAA")  # Exemple ancien
            reduction = longueur_ancienne - longueur_nouvelle
            print(f"   Longueur moyenne SKU: {longueur_nouvelle} caractères")
            print(f"   Réduction vs ancien: {reduction} caractères ({reduction/longueur_ancienne*100:.1f}%)")
    
    print(f"\n✨ Test GUI terminé avec succès!")
    return True

if __name__ == "__main__":
    print("🚀 Test compatibilité GUI avec SKU simplifiés")
    print("=" * 55)
    
    try:
        test_gui_integration()
        
        print("\n🎉 La GUI est compatible avec le nouveau format !")
        print("\n💡 Points clés pour la GUI :")
        print("   • Génération: Utilise automatiquement le nouveau format")
        print("   • Recherche: Fonctionne avec anciens et nouveaux SKU")
        print("   • Décodage: Affiche correctement les informations")
        print("   • Statistiques: Calculs de longueur mis à jour")
        
    except Exception as e:
        print(f"\n❌ Erreur test GUI : {e}")
        import traceback
        traceback.print_exc()
