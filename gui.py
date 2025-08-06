#!/usr/bin/env python3
"""
Interface utilisateur simple pour le générateur de SKU
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
from pathlib import Path
import threading
import sys
import os

# Ajouter le répertoire courant au path pour importer nos modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sku_generator import SKUGenerator, Component
from main import BOMProcessor
from bom_analyzer import BOMComparator

class SKUGeneratorGUI:
    """Interface graphique pour le générateur de SKU"""

    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de SKU Industriel - Noovelia")
        self.root.geometry("800x600")

        # Variables
        self.generator = SKUGenerator()
        self.processor = BOMProcessor(self.generator)
        self.comparator = BOMComparator(self.generator)

        self.create_widgets()
        self.update_stats()

    def create_widgets(self):
        """Créer l'interface utilisateur"""

        # Titre
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(title_frame, text="Générateur de SKU Industriel",
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(title_frame, text="Avec logique de Route et Routing",
                 font=("Arial", 10)).pack()

        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Section statistiques
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiques Base de Données")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_text = ttk.Label(stats_frame, text="Chargement...")
        self.stats_text.pack(padx=10, pady=5)

        # Section traitement
        process_frame = ttk.LabelFrame(main_frame, text="Traitement BOM")
        process_frame.pack(fill=tk.X, pady=(0, 10))

        # Boutons
        button_frame = ttk.Frame(process_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="📁 Analyser nouveau BOM",
                  command=self.analyze_bom).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⚙️ Traiter et générer SKU",
                  command=self.process_bom).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔄 Actualiser stats",
                  command=self.update_stats).pack(side=tk.LEFT)

        # Zone de résultats
        results_frame = ttk.LabelFrame(main_frame, text="Résultats")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Barre de progression
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(5, 0))

    def log_result(self, message):
        """Ajouter un message aux résultats"""
        self.results_text.insert(tk.END, message + "\\n")
        self.results_text.see(tk.END)
        self.root.update()

    def update_stats(self):
        """Mettre à jour les statistiques"""
        try:
            stats = self.comparator.get_database_stats()

            stats_text = f"📊 Total: {stats['total']} composants | "
            if stats['par_domaine']:
                domain_stats = [f"{domain}: {count}" for domain, count in stats['par_domaine'].items()]
                stats_text += " | ".join(domain_stats)

            self.stats_text.config(text=stats_text)

        except Exception as e:
            self.stats_text.config(text=f"❌ Erreur: {str(e)}")

    def analyze_bom(self):
        """Analyser un nouveau BOM"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier BOM",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not file_path:
            return

        def analyze_thread():
            try:
                self.progress.start()
                self.log_result(f"🔍 Analyse du fichier: {Path(file_path).name}")

                analysis = self.comparator.analyze_new_bom(file_path)

                self.log_result("\\n📈 RÉSULTATS DE L'ANALYSE:")
                self.log_result(f"  Composants NOUVEAUX: {analysis['nouveau']}")
                self.log_result(f"  Composants EXISTANTS: {analysis['existant']}")
                self.log_result(f"  Total analysé: {analysis['nouveau'] + analysis['existant']}")

                for domain, details in analysis['details'].items():
                    if details:
                        self.log_result(f"\\n🔧 {domain.upper()}:")
                        self.log_result(f"  Nouveaux: {details['nouveau']}")
                        self.log_result(f"  Existants: {details['existant']}")

                        if details['composants_existants']:
                            self.log_result("  Exemples de composants existants:")
                            for comp in details['composants_existants'][:3]:
                                self.log_result(f"    - {comp['nom']} → {comp['sku_existant']}")

                        if details['composants_nouveaux']:
                            self.log_result("  Exemples de nouveaux composants:")
                            for comp in details['composants_nouveaux'][:3]:
                                self.log_result(f"    - {comp['nom']} ({comp['type']})")

                self.log_result("\\n✅ Analyse terminée")

            except Exception as e:
                self.log_result(f"❌ Erreur lors de l'analyse: {str(e)}")
            finally:
                self.progress.stop()

        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()

    def process_bom(self):
        """Traiter un BOM et générer les SKU"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier BOM à traiter",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not file_path:
            return

        def process_thread():
            try:
                self.progress.start()
                self.log_result(f"⚙️ Traitement du fichier: {Path(file_path).name}")

                # Traiter le fichier
                results = self.processor.process_bom_file(file_path)

                # Générer le nom de fichier de sortie
                input_name = Path(file_path).stem
                output_file = f"SKU_{input_name}.xlsx"

                # Exporter les résultats
                self.processor.export_results(results, output_file)

                # Afficher le résumé
                self.log_result("\\n📋 RÉSULTATS DU TRAITEMENT:")
                total_components = 0

                for domain, df in results.items():
                    count = len(df)
                    total_components += count
                    self.log_result(f"  {domain}: {count} composants")

                    # Afficher quelques exemples de SKU
                    self.log_result(f"  Exemples de SKU {domain}:")
                    for sku in df['SKU'].head(3):
                        self.log_result(f"    - {sku}")
                    self.log_result("")

                self.log_result(f"📊 TOTAL: {total_components} composants traités")
                self.log_result(f"💾 Résultats sauvegardés: {output_file}")
                self.log_result("✅ Traitement terminé")

                # Mettre à jour les statistiques
                self.update_stats()

                # Proposer d'ouvrir le fichier
                if messagebox.askyesno("Traitement terminé",
                                     f"Le traitement est terminé.\\n\\nVoulez-vous ouvrir le fichier de résultats?\\n{output_file}"):
                    os.startfile(output_file)

            except Exception as e:
                self.log_result(f"❌ Erreur lors du traitement: {str(e)}")
            finally:
                self.progress.stop()

        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = SKUGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
