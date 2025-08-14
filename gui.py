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
from queue import Queue, Empty

# Ajouter le répertoire courant au path pour importer nos modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sku_generator import SKUGenerator, Component
from main import BOMProcessor
from bom_analyzer import BOMComparator
from component_validation_window import ComponentValidationWindow
from odoo_integration import ODOOIntegration

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
        self.odoo_integration = ODOOIntegration()

        # File dialog: remember last directory (session only)
        self._last_dir = os.getcwd()

        # Thread-safe logging queue
        self._log_queue = Queue()

        self.create_widgets()
        self.update_stats()

        # Start log queue processor on UI thread
        self.root.after(100, self._process_log_queue)

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
                   command=self.update_stats).pack(side=tk.LEFT, padx=(0, 5))
        # Fix label characters for Windows fonts
        ttk.Button(button_frame, text="📤 Export ODOO",
                   command=self.export_odoo_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ Effacer résultats",
                   command=self.clear_results).pack(side=tk.LEFT)

        # Section recherche
        search_frame = ttk.LabelFrame(main_frame, text="Recherche par SKU")
        search_frame.pack(fill=tk.X, pady=(10, 10))

        # Frame pour la recherche
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_input_frame, text="SKU:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(search_input_frame, width=30, font=("Consolas", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_sku())

        ttk.Button(search_input_frame, text="🔍 Rechercher",
                   command=self.search_sku).pack(side=tk.LEFT, padx=(5, 0))

        # Zone de résultats
        results_frame = ttk.LabelFrame(main_frame, text="Résultats")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=15,
                                                      font=("Consolas", 10),
                                                      wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configuration des couleurs pour améliorer la lisibilité
        self.setup_text_formatting()

        # Barre de progression
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(5, 0))

    def setup_text_formatting(self):
        """Configuration des styles de texte pour améliorer la lisibilité"""
        # Couleurs et styles
        self.results_text.tag_configure("header",
                                       foreground="#2E8B57",
                                       font=("Consolas", 11, "bold"))
        self.results_text.tag_configure("success",
                                       foreground="#228B22",
                                       font=("Consolas", 10, "bold"))
        self.results_text.tag_configure("error",
                                       foreground="#DC143C",
                                       font=("Consolas", 10, "bold"))
        self.results_text.tag_configure("info",
                                       foreground="#4169E1",
                                       font=("Consolas", 10))
        self.results_text.tag_configure("highlight",
                                       foreground="#FF8C00",
                                       font=("Consolas", 10, "bold"))
        self.results_text.tag_configure("sku",
                                       foreground="#8B008B",
                                       font=("Consolas", 10, "bold"))
        self.results_text.tag_configure("separator",
                                       foreground="#696969",
                                       font=("Consolas", 10))

    def log_header(self, title):
        """Ajouter un en-tête avec séparateur (thread-safe)"""
        separator = "=" * 60
        self._enqueue_log(f"\n{separator}\n", "separator")
        self._enqueue_log(f"{title}\n", "header")
        self._enqueue_log(f"{separator}\n", "separator")

    def log_section(self, title):
        """Ajouter une section avec formatage (thread-safe)"""
        self._enqueue_log(f"\n📋 {title}\n", "highlight")
        self._enqueue_log("-" * 40 + "\n", "separator")

    def log_success(self, message):
        """Ajouter un message de succès (thread-safe)"""
        self._enqueue_log(f"✅ {message}\n", "success")

    def log_error(self, message):
        """Ajouter un message d'erreur (thread-safe)"""
        self._enqueue_log(f"❌ {message}\n", "error")

    def log_info(self, message):
        """Ajouter un message d'information (thread-safe)"""
        self._enqueue_log(f"ℹ️  {message}\n", "info")

    def log_sku_example(self, name, sku):
        """Afficher un exemple de SKU (thread-safe)"""
        self._enqueue_log(f"    • {name:<25} → ", "info")
        self._enqueue_log(f"{sku}\n", "sku")

    def clear_results(self):
        """Effacer la zone de résultats (thread-safe)"""
        self.root.after(0, lambda: self.results_text.delete(1.0, tk.END))

    # ---------- Thread-safe helpers ----------
    def _enqueue_log(self, text: str, tag: str = "info"):
        """Place a log message into the queue to be processed on UI thread."""
        self._log_queue.put((text, tag))

    def _process_log_queue(self):
        """Flush queued log messages on the UI thread."""
        try:
            while True:
                text, tag = self._log_queue.get_nowait()
                self.results_text.insert(tk.END, text, tag)
                self.results_text.see(tk.END)
        except Empty:
            pass
        finally:
            # keep polling
            self.root.after(100, self._process_log_queue)

    def _progress_start(self):
        self.root.after(0, self.progress.start)

    def _progress_stop(self):
        self.root.after(0, self.progress.stop)

    def check_file_access(self, file_path):
        """Vérifier l'accès au fichier avant traitement"""
        try:
            # Tenter d'ouvrir le fichier en lecture
            with open(file_path, 'rb') as f:
                f.read(1024)  # Lire quelques octets pour tester
            return True, None
        except PermissionError:
            return False, "Fichier verrouillé ou permissions insuffisantes"
        except FileNotFoundError:
            return False, "Fichier non trouvé"
        except Exception as e:
            return False, f"Erreur d'accès: {str(e)}"

    def log_result(self, message):
        """Ajouter un message aux résultats (méthode héritée, utilise log_info)"""
        self.log_info(message)

    def update_stats(self):
        """Mettre à jour les statistiques"""
        try:
            stats = self.comparator.get_database_stats()

            stats_text = f"📊 Total: {stats['total']} composants | "
            if stats['par_domaine']:
                domain_stats = [f"{domain}: {count}" for domain, count in stats['par_domaine'].items()]
                stats_text += " | ".join(domain_stats)

            # UI update on main thread
            self.root.after(0, lambda: self.stats_text.config(text=stats_text))

        except Exception as e:
            self.root.after(0, lambda: self.stats_text.config(text=f"❌ Erreur: {str(e)}"))

    def analyze_bom(self):
        """Analyser un nouveau BOM"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier BOM",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir=self._last_dir,
        )

        if not file_path:
            return
        # remember last dir
        self._last_dir = os.path.dirname(file_path)

        def analyze_thread():
            try:
                self._progress_start()
                self.clear_results()

                # En-tête principal
                self.log_header(f"🔍 ANALYSE BOM: {Path(file_path).name}")

                # Vérification préalable du fichier
                self.log_info(f"Fichier: {file_path}")
                self.log_info("Vérification d'accès au fichier...")

                can_access, error_msg = self.check_file_access(file_path)
                if not can_access:
                    self.log_error(f"Impossible d'accéder au fichier: {error_msg}")
                    self.log_info("💡 Solutions possibles:")
                    self.log_info("   1. Fermez le fichier s'il est ouvert dans Excel")
                    self.log_info("   2. Attendez que OneDrive finisse la synchronisation")
                    self.log_info("   3. Copiez le fichier dans un autre dossier")
                    self.log_info("   4. Vérifiez les permissions du fichier")
                    return

                self.log_success("Accès au fichier confirmé!")
                self.log_info("Analyse en cours...")

                analysis = self.comparator.analyze_new_bom(file_path)

                # Résultats principaux
                self.log_section("RÉSULTATS GLOBAUX")
                self.log_info(f"📊 Composants NOUVEAUX: {analysis['nouveau']}")
                self.log_info(f"📊 Composants EXISTANTS: {analysis['existant']}")
                self.log_info(f"📊 Total analysé: {analysis['nouveau'] + analysis['existant']}")

                # Détails par domaine
                for domain, details in analysis['details'].items():
                    if details and (details['nouveau'] > 0 or details['existant'] > 0):
                        self.log_section(f"DÉTAILS {domain.upper()}")
                        self.log_info(f"🔧 Nouveaux: {details['nouveau']}")
                        self.log_info(f"🔧 Existants: {details['existant']}")

                        if details['composants_existants']:
                            self.log_info("\\n📋 Exemples de composants existants:")
                            for comp in details['composants_existants'][:5]:
                                self.log_sku_example(comp['nom'], comp['sku_existant'])

                        if details['composants_nouveaux']:
                            self.log_info("\\n🆕 Exemples de nouveaux composants:")
                            for comp in details['composants_nouveaux'][:5]:
                                self.log_info(f"    • {comp['nom']} ({comp['type']})")

                self.log_success("Analyse terminée avec succès!")

            except PermissionError as e:
                self.log_error("Accès au fichier refusé!")
                self.log_info("💡 Solutions possibles:")
                self.log_info("   1. Fermez le fichier s'il est ouvert dans Excel")
                self.log_info("   2. Attendez que OneDrive finisse la synchronisation")
                self.log_info("   3. Copiez le fichier dans un autre dossier")
                self.log_info("   4. Vérifiez les permissions du fichier")
                self.log_info(f"\\n📁 Fichier concerné: {Path(file_path).name}")
            except FileNotFoundError as e:
                self.log_error(f"Fichier non trouvé: {Path(file_path).name}")
                self.log_info("💡 Vérifiez que le fichier existe toujours")
            except Exception as e:
                self.log_error(f"Erreur lors de l'analyse: {str(e)}")
                self.log_info("💡 Vérifiez le format du fichier Excel")
            finally:
                self._progress_stop()

        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()

    def process_bom(self):
        """Traiter un BOM et générer les SKU"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier BOM à traiter",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir=self._last_dir,
        )

        if not file_path:
            return
        self._last_dir = os.path.dirname(file_path)

        def process_thread():
            try:
                self._progress_start()
                self.clear_results()

                # En-tête principal
                self.log_header(f"⚙️ TRAITEMENT BOM: {Path(file_path).name}")

                # Vérification préalable du fichier
                self.log_info(f"Fichier: {file_path}")
                self.log_info("Vérification d'accès au fichier...")

                can_access, error_msg = self.check_file_access(file_path)
                if not can_access:
                    self.log_error(f"Impossible d'accéder au fichier: {error_msg}")
                    self.log_info("💡 Solutions possibles:")
                    self.log_info("   1. Fermez le fichier s'il est ouvert dans Excel")
                    self.log_info("   2. Attendez que OneDrive finisse la synchronisation")
                    self.log_info("   3. Copiez le fichier dans un autre dossier")
                    self.log_info("   4. Vérifiez les permissions du fichier")
                    return

                self.log_success("Accès au fichier confirmé!")
                self.log_info("Traitement en cours...")

                # Traiter le fichier
                # D'abord extraire tous les composants pour validation
                self.log_info("Extraction des composants pour validation...")
                components_by_domain = self.processor.extract_components_from_bom(file_path)

                if not components_by_domain:
                    self.log_error("Aucun composant valide trouvé dans le fichier")
                    return

                # Afficher la fenêtre de validation
                self._progress_stop()
                self.show_validation_window(components_by_domain, file_path)

            except PermissionError:
                self.log_error("Fichier en cours d'utilisation ou accès refusé")
                self.log_info("💡 Fermez le fichier Excel et réessayez")
            except Exception as e:
                self.log_error(f"Erreur lors du traitement: {str(e)}")
            finally:
                self._progress_stop()

        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

    def show_validation_window(self, components_by_domain, file_path):
        """Afficher la fenêtre de validation des composants"""
        def on_validation_complete(selected_components):
            """Callback après validation des composants"""
            self.process_validated_components(selected_components, file_path)

        # Créer et afficher la fenêtre de validation
        validation_window = ComponentValidationWindow(
            self.root,
            components_by_domain,
            file_path,
            callback=on_validation_complete
        )

    def process_validated_components(self, selected_components, file_path):
        """Traiter les composants validés et générer les SKU"""
        def process_thread():
            try:
                self._progress_start()

                # En-tête principal
                self.log_header(f"⚙️ GÉNÉRATION DES SKU")
                self.log_info(f"Fichier: {Path(file_path).name}")

                # Générer les SKU pour les composants sélectionnés
                results = self.processor.generate_skus_for_selected_components(selected_components)

                # Générer le nom de fichier de sortie
                input_name = Path(file_path).stem
                output_file = f"SKU_{input_name}.xlsx"

                # Exporter les résultats
                self.processor.export_results(results, output_file)

                # Export ODOO automatique
                try:
                    odoo_count, odoo_file = self.odoo_integration.export_to_odoo_csv(results, f"ODOO_{output_file}")
                    self.log_info(f"📤 Export ODOO: {odoo_count} produits → {odoo_file}")
                except Exception as e:
                    self.log_error(f"Erreur export ODOO: {str(e)}")

                # Afficher le résumé par domaine
                self.log_section("RÉSULTATS DU TRAITEMENT")
                total_components = 0

                for domain, df in results.items():
                    count = len(df)
                    total_components += count

                    self.log_info(f"🔧 {domain}: {count} composants traités")

                self.log_success(f"✅ TRAITEMENT TERMINÉ: {total_components} composants")
                self.log_info(f"📁 Fichier généré: {output_file}")

                # Mettre à jour les statistiques
                self.update_stats()

                # Proposer d'ouvrir le fichier généré
                def _ask_open():
                    if messagebox.askyesno(
                        "Traitement terminé",
                        f"Le traitement est terminé avec succès!\n\n📊 {total_components} composants traités\n💾 Fichier: {output_file}\n\nVoulez-vous ouvrir le fichier de résultats?"
                    ):
                        try:
                            os.startfile(output_file)
                        except Exception as ex:
                            messagebox.showerror("Ouverture fichier", f"Impossible d'ouvrir le fichier: {ex}")
                self.root.after(0, _ask_open)

            except Exception as e:
                self.log_error(f"Erreur lors de la génération des SKU: {str(e)}")
            finally:
                self._progress_stop()

        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

    def process_bom_old(self):
        """Ancienne méthode de traitement BOM (pour référence)"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier BOM à traiter",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir=self._last_dir,
        )

        if not file_path:
            return
        self._last_dir = os.path.dirname(file_path)

        def process_thread():
            try:
                self._progress_start()
                self.clear_results()

                # En-tête principal
                self.log_header(f"⚙️ TRAITEMENT BOM: {Path(file_path).name}")

                # Vérification préalable du fichier
                self.log_info(f"Fichier: {file_path}")
                self.log_info("Vérification d'accès au fichier...")

                can_access, error_msg = self.check_file_access(file_path)
                if not can_access:
                    self.log_error(f"Impossible d'accéder au fichier: {error_msg}")
                    self.log_info("💡 Solutions possibles:")
                    self.log_info("   1. Fermez le fichier s'il est ouvert dans Excel")
                    self.log_info("   2. Attendez que OneDrive finisse la synchronisation")
                    self.log_info("   3. Copiez le fichier dans un autre dossier")
                    self.log_info("   4. Vérifiez les permissions du fichier")
                    return

                self.log_success("Accès au fichier confirmé!")
                self.log_info("Traitement en cours...")

                # Traiter le fichier
                results = self.processor.process_bom_file(file_path)

                # Générer le nom de fichier de sortie
                input_name = Path(file_path).stem
                output_file = f"SKU_{input_name}.xlsx"

                # Exporter les résultats
                self.processor.export_results(results, output_file)

                # Afficher le résumé par domaine
                self.log_section("RÉSULTATS DU TRAITEMENT")
                total_components = 0

                for domain, df in results.items():
                    count = len(df)
                    total_components += count

                    self.log_info(f"🔧 {domain}: {count} composants traités")

                    # Afficher quelques exemples de SKU avec formatage
                    self.log_info(f"\\n📋 Exemples de SKU {domain}:")
                    for _, row in df.head(5).iterrows():
                        self.log_sku_example(row['Name'], row['SKU'])

                # Résumé final
                self.log_section("RÉSUMÉ FINAL")
                self.log_info(f"📊 TOTAL: {total_components} composants traités")
                self.log_info(f"💾 Fichier généré: {output_file}")

                # Mettre à jour les statistiques
                self.update_stats()

                self.log_success("Traitement terminé avec succès!")

                # Proposer d'ouvrir le fichier
                if messagebox.askyesno("Traitement terminé",
                                     f"Le traitement est terminé avec succès!\\n\\n📊 {total_components} composants traités\\n💾 Fichier: {output_file}\\n\\nVoulez-vous ouvrir le fichier de résultats?"):
                    os.startfile(output_file)

            except PermissionError as e:
                self.log_error("Accès au fichier refusé!")
                self.log_info("💡 Solutions possibles:")
                self.log_info("   1. Fermez le fichier s'il est ouvert dans Excel")
                self.log_info("   2. Attendez que OneDrive finisse la synchronisation")
                self.log_info("   3. Copiez le fichier dans un autre dossier")
                self.log_info("   4. Vérifiez les permissions du fichier")
                self.log_info(f"\\n📁 Fichier concerné: {Path(file_path).name}")
            except FileNotFoundError as e:
                self.log_error(f"Fichier non trouvé: {Path(file_path).name}")
                self.log_info("💡 Vérifiez que le fichier existe toujours")
            except Exception as e:
                self.log_error(f"Erreur lors du traitement: {str(e)}")
                self.log_info("💡 Vérifiez le format du fichier Excel")
            finally:
                self._progress_stop()

        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

    def search_sku(self):
        """Rechercher un composant par son SKU"""
        sku = self.search_entry.get().strip().upper()

        if not sku:
            messagebox.showwarning("Recherche", "Veuillez entrer un SKU à rechercher")
            return

        def search_thread():
            try:
                self._progress_start()
                self.clear_results()

                # En-tête principal
                self.log_header(f"🔍 RECHERCHE SKU: {sku}")

                self.log_info(f"Recherche du SKU: {sku}")
                self.log_info("Consultation de la base de données...")

                # Rechercher dans la base de données
                result = self.generator.search_component_by_sku(sku)

                if result:
                    self.log_success("Composant trouvé!")

                    # Afficher les informations du composant (améliorées)
                    self.log_section("INFORMATIONS DU COMPOSANT")
                    self.log_info(f"📦 Nom            : {result['nom']}")

                    # Description si disponible
                    if result.get('description'):
                        self.log_info(f"🧠 Description    : {result['description']}")

                    self.log_info(f"🏷️  SKU            : {result['sku']}")
                    self.log_info(f"🏭 Domaine        : {result['domaine']}")

                    # Informations fabricant si disponibles
                    if result.get('fabricant'):
                        self.log_info(f"🏢 Fabricant      : {result['fabricant']}")
                    if result.get('ref_fabricant'):
                        self.log_info(f"📋 Réf. fabricant : {result['ref_fabricant']}")

                    self.log_info(f"📅 Date création  : {result['date_creation']}")

                    # Section décodage améliorée
                    self.log_section(f"STRUCTURE SKU ({result['sku']})")

                    # Décoder le SKU avec les nouvelles méthodes
                    decoded = self.generator.decode_sku_parts(result['sku'])
                    if decoded:
                        fmt = decoded.get('format')
                        if fmt == 'ancien':
                            # Ancien format: DOMAINE-ROUTE-ROUTING-TYPE-SEQUENCE
                            self.log_info(f"🏭 Domaine   : {decoded['domaine_code']} → {decoded['domaine_nom']}")
                            process_desc = self.generator.get_process_description(
                                decoded['domaine_code'], decoded['route_code'], decoded['routing_code']
                            )
                            self.log_info(f"🛠️  Processus : {process_desc}")
                            self.log_info(f"🛣️  Route     : {decoded['route_code']} → {decoded['route_nom']}")
                            self.log_info(f"⚙️ Routing   : {decoded['routing_code']} → {decoded['routing_nom']}")
                            self.log_info(f"🔧 Type      : {decoded['type_code']} → {decoded['type_nom']}")
                            self.log_info(f"🔢 Index     : {decoded['sequence']}")
                        elif fmt == 'simplifie':
                            # Nouveau format simplifié: FAMILLE-SOUS_FAMILLE-SEQUENCE
                            self.log_info(f"🏭 Famille   : {decoded['famille_code']} → {decoded['famille_nom']}")
                            self.log_info(f"🔧 Type      : {decoded['sous_famille_code']} → {decoded['sous_famille_nom']}")
                            self.log_info(f"🔢 Index     : {decoded['sequence']}")
                            # Description simple
                            self.log_info(f"📝 Description : {decoded.get('description', '')}")
                        else:
                            # Format invalide
                            self.log_error(decoded.get('erreur', 'Format SKU invalide'))
                    else:
                        # Fallback si le décodage échoue
                        sku_parts = result['sku'].split('-')
                        if len(sku_parts) == 5:
                            self.log_info(f"🏭 Domaine: {sku_parts[0]} ({result['domaine']})")
                            self.log_info(f"🛣️  Route: {sku_parts[1]} ({result['route']})")
                            self.log_info(f"⚙️ Routing: {sku_parts[2]} ({result['routing']})")
                            self.log_info(f"🔧 Type: {sku_parts[3]} ({result['type']})")
                            self.log_info(f"📊 Séquence: {sku_parts[4]}")
                        elif len(sku_parts) == 3:
                            self.log_info(f"🏭 Famille: {sku_parts[0]}")
                            self.log_info(f"🔧 Type   : {sku_parts[1]}")
                            self.log_info(f"📊 Séquence: {sku_parts[2]}")

                    # Rechercher des composants similaires
                    self.log_section("COMPOSANTS SIMILAIRES")
                    similar = self.generator.find_similar_components(result['domaine'], result['type'])
                    if similar:
                        similar_count = len([comp for comp in similar if comp['sku'] != sku])
                        if similar_count > 0:
                            self.log_info(f"Trouvé {similar_count} composant(s) similaire(s) du même type:")
                            for comp in similar[:8]:  # Limiter à 8 résultats
                                if comp['sku'] != sku:  # Exclure le composant recherché
                                    self.log_sku_example(comp['nom'], comp['sku'])
                        else:
                            self.log_info("Aucun autre composant similaire du même type")
                    else:
                        self.log_info("Aucun composant similaire trouvé")

                else:
                    self.log_error("SKU non trouvé dans la base de données")
                    self.log_info("💡 Vérifications possibles:")
                    self.log_info("   1. Vérifiez l'orthographe du SKU")
                    self.log_info("   2. Assurez-vous que le composant a été traité")
                    self.log_info("   3. Formats acceptés: DOMAINE-ROUTE-ROUTING-TYPE-SEQUENCE ou FAMILLE-SOUS_FAMILLE-SEQUENCE")

                    # Proposer une recherche partielle
                    if '-' in sku:
                        self.log_info("\\n🔍 Recherche de SKU similaires...")
                        partial_results = self.generator.search_partial_sku(sku)
                        if partial_results:
                            self.log_section("SKU SIMILAIRES TROUVÉS")
                            for comp in partial_results[:10]:
                                self.log_sku_example(comp['nom'], comp['sku'])
                        else:
                            self.log_info("Aucun SKU similaire trouvé")

            except Exception as e:
                self.log_error(f"Erreur lors de la recherche: {str(e)}")
                self.log_info("💡 Vérifiez le format du SKU ou contactez l'administrateur")
            finally:
                self._progress_stop()

        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()

    def export_odoo_template(self):
        """Créer un template d'import pour ODOO"""
        try:
            template_file = self.odoo_integration.create_import_template()

            self.clear_results()
            self.log_header("📤 TEMPLATE ODOO CRÉÉ")
            self.log_success(f"Template généré: {template_file}")
            self.log_info("📋 Le template contient:")
            self.log_info("  • Feuille 'Exemples' avec des données d'exemple")
            self.log_info("  • Feuille 'Import_ODOO' vide pour vos données")
            self.log_info("  • Feuille 'Documentation' avec les descriptions")
            self.log_info("")
            self.log_info("🎯 Utilisation:")
            self.log_info("  1. Remplissez la feuille 'Import_ODOO'")
            self.log_info("  2. Importez dans ODOO via Inventaire > Produits")
            self.log_info("  3. Utilisez le format CSV avec séparateur ';'")

            # Proposer d'ouvrir
            if messagebox.askyesno("Template créé",
                                 f"Template ODOO créé avec succès!\n\nFichier: {template_file}\n\nVoulez-vous l'ouvrir?"):
                os.startfile(template_file)

        except Exception as e:
            self.log_error(f"Erreur lors de la création du template: {str(e)}")

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = SKUGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
