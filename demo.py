#!/usr/bin/env python3
"""
Script de démonstration et test du générateur de SKU
"""

import pandas as pd
from sku_generator import SKUGenerator, Component
from main import BOMProcessor
from bom_analyzer import BOMComparator
import logging

def demo_sku_generation():
    """Démonstration de génération de SKU individuels"""
    print("="*60)
    print("DÉMONSTRATION - GÉNÉRATION DE SKU INDIVIDUELS")
    print("="*60)

    generator = SKUGenerator()

    # Exemples de composants électriques
    electrical_components = [
        Component(
            name="Connecteur USB-C",
            description="Connecteur USB Type-C",
            domain="ELEC",
            component_type="Connecteurs",
            route="",
            routing=""
        ),
        Component(
            name="Résistance 10K",
            description="Résistance 10KΩ 1/4W",
            domain="ELEC",
            component_type="Resistances",
            route="",
            routing=""
        ),
        Component(
            name="Microcontrôleur STM32",
            description="Microcontrôleur ARM Cortex-M4",
            domain="ELEC",
            component_type="Controleurs",
            route="",
            routing=""
        )
    ]

    # Exemples de composants mécaniques
    mechanical_components = [
        Component(
            name="Vis M4x16",
            description="Vis à tête hexagonale M4x16mm",
            domain="MECA",
            component_type="015 | BOULONNERIE",
            route="",
            routing=""
        ),
        Component(
            name="Plaque support",
            description="Plaque support en aluminium",
            domain="MECA",
            component_type="121 | PIÈCES PLIÉES",
            route="",
            routing=""
        ),
        Component(
            name="Axe usiné",
            description="Axe usiné en acier inox",
            domain="MECA",
            component_type="131 | PIÈCES USINÉES",
            route="",
            routing=""
        )
    ]

    print("🔧 COMPOSANTS ÉLECTRIQUES:")
    for comp in electrical_components:
        sku = generator.generate_sku(comp)
        print(f"  {comp.name:<25} → {sku}")

    print("\\n⚙️ COMPOSANTS MÉCANIQUES:")
    for comp in mechanical_components:
        sku = generator.generate_sku(comp)
        print(f"  {comp.name:<25} → {sku}")

    print("\\n✅ Démonstration terminée")

def demo_duplicate_detection():
    """Démonstration de détection des doublons"""
    print("\\n" + "="*60)
    print("DÉMONSTRATION - DÉTECTION DES DOUBLONS")
    print("="*60)

    generator = SKUGenerator()

    # Créer le même composant deux fois
    component1 = Component(
        name="Vis M6x20",
        description="Vis à tête cylindrique",
        domain="MECA",
        component_type="015 | BOULONNERIE",
        route="",
        routing="",
        manufacturer="ACME Corp"
    )

    component2 = Component(
        name="Vis M6x20",
        description="Vis à tête cylindrique",  # Même description
        domain="MECA",
        component_type="015 | BOULONNERIE",
        route="",
        routing="",
        manufacturer="ACME Corp"  # Même fabricant
    )

    print("🔍 Test de détection des doublons:")
    print(f"Composant 1: {component1.name}")
    sku1 = generator.generate_sku(component1)
    print(f"  SKU généré: {sku1}")

    print(f"\\nComposant 2 (identique): {component2.name}")
    sku2 = generator.generate_sku(component2)
    print(f"  SKU récupéré: {sku2}")

    if sku1 == sku2:
        print("\\n✅ Détection des doublons fonctionne - Même SKU réutilisé")
    else:
        print("\\n❌ Problème - SKU différents générés")

def demo_routing_logic():
    """Démonstration de la logique de routing"""
    print("\\n" + "="*60)
    print("DÉMONSTRATION - LOGIQUE DE ROUTE ET ROUTING")
    print("="*60)

    generator = SKUGenerator()

    # Différents types de routings
    routing_examples = [
        {
            "name": "Pièce assemblée",
            "type": "Assemblage",
            "domain": "ELEC",
            "expected_route": "ASS",
            "expected_routing": "ASM"
        },
        {
            "name": "Borne de connexion",
            "type": "Borniers",
            "domain": "ELEC",
            "expected_route": "TERM",
            "expected_routing": "STD"
        },
        {
            "name": "Pièce pliée",
            "type": "121 | PIÈCES PLIÉES",
            "domain": "MECA",
            "expected_route": "BEND",
            "expected_routing": "BEND"
        },
        {
            "name": "Découpe laser",
            "type": "111 | PIÈCES DÉCOUPÉES LASER",
            "domain": "MECA",
            "expected_route": "LASER",
            "expected_routing": "CUT"
        }
    ]

    print("🎯 Exemples de logique Route/Routing:")
    for example in routing_examples:
        component = Component(
            name=example["name"],
            description=f"Test {example['name']}",
            domain=example["domain"],
            component_type=example["type"],
            route="",
            routing=""
        )

        # Générer le SKU et analyser sa structure
        sku = generator.generate_sku(component)
        parts = sku.split('-')

        print(f"\\n  {example['name']:<20}")
        print(f"    Type: {example['type']}")
        print(f"    SKU: {sku}")
        print(f"    Route: {parts[1]} (attendu: {example['expected_route']})")
        print(f"    Routing: {parts[2]} (attendu: {example['expected_routing']})")

def demo_statistics():
    """Démonstration des statistiques"""
    print("\\n" + "="*60)
    print("DÉMONSTRATION - STATISTIQUES DE LA BASE DE DONNÉES")
    print("="*60)

    generator = SKUGenerator()
    comparator = BOMComparator(generator)

    try:
        stats = comparator.get_database_stats()

        print("📊 STATISTIQUES GÉNÉRALES:")
        print(f"  Total composants: {stats['total']}")

        if stats['par_domaine']:
            print("\\n📈 RÉPARTITION PAR DOMAINE:")
            for domain, count in stats['par_domaine'].items():
                print(f"  {domain}: {count} composants")

        if stats['par_route']:
            print("\\n🛣️ TOP 10 ROUTES:")
            for route, count in list(stats['par_route'].items())[:10]:
                if route:  # Ignorer les routes vides
                    print(f"  {route}: {count} composants")

        if stats['par_routing']:
            print("\\n⚙️ TOP 10 ROUTINGS:")
            for routing, count in list(stats['par_routing'].items())[:10]:
                if routing:  # Ignorer les routings vides
                    print(f"  {routing}: {count} composants")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")

def main():
    """Fonction principale de démonstration"""
    logging.basicConfig(level=logging.WARNING)  # Réduire les logs pour la démo

    print("🚀 DÉMONSTRATION COMPLÈTE DU GÉNÉRATEUR DE SKU INDUSTRIEL")
    print("Développé pour Noovelia avec logique de Route et Routing")

    # Démonstrations
    demo_sku_generation()
    demo_duplicate_detection()
    demo_routing_logic()
    demo_statistics()

    print("\\n" + "="*60)
    print("🎉 DÉMONSTRATION TERMINÉE")
    print("="*60)
    print("💡 Pour utiliser le système:")
    print("  - Interface graphique: python gui.py")
    print("  - Traitement BOM: python main.py")
    print("  - Analyse BOM: python bom_analyzer.py")
    print("\\n📚 Documentation complète dans README.md")

if __name__ == "__main__":
    main()
