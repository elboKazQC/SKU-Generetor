#!/usr/bin/env python3
"""
Fenêtre de validation des composants avant génération des SKU
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from pathlib import Path
from typing import Dict, List
from sku_generator import Component, SKUGenerator


class ComponentValidationWindow:
    """Fenêtre pour valider et sélectionner les composants avant génération des SKU"""

    def __init__(self, parent, components_data: Dict[str, List[Component]], file_path: str, callback=None):
        self.parent = parent
        self.components_data = components_data
        self.file_path = file_path
        self.callback = callback
        self.selected_components = {}  # Stocker les composants sélectionnés
        self.component_vars = {}  # Variables de checkbox
        self.sku_generator = SKUGenerator()  # Pour l'aperçu des SKU

        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("Validation des Composants - Génération SKU")
        self.window.geometry("1200x800")
        self.window.transient(parent)
        self.window.grab_set()  # Modal

        # Initialiser les composants sélectionnés (tous par défaut)
        for domain, components in components_data.items():
            self.selected_components[domain] = components.copy()

        self.create_widgets()
        self.populate_components()

        # Centrer la fenêtre
        self.center_window()

    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Créer l'interface de validation"""

        # En-tête
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(header_frame, text="🔍 Validation des Composants",
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(header_frame, text=f"Fichier: {Path(self.file_path).name}",
                 font=("Arial", 10)).pack()
        ttk.Label(header_frame, text="Cliquez sur les lignes pour sélectionner/désélectionner les composants",
                 font=("Arial", 10, "italic")).pack(pady=5)

        # Frame pour les statistiques
        stats_frame = ttk.LabelFrame(self.window, text="Statistiques")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack(pady=5)

        # Notebook pour les onglets par domaine (retour à l'interface simple)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame pour les boutons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Boutons de sélection globale
        ttk.Button(button_frame, text="✅ Tout sélectionner",
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Tout désélectionner",
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)

        # Spacer
        ttk.Label(button_frame, text="").pack(side=tk.LEFT, expand=True)

        # Boutons d'action
        ttk.Button(button_frame, text="❌ Annuler",
                  command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="✅ Générer les SKU",
                  command=self.confirm, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

    def populate_components(self):
        """Remplir les onglets avec les composants"""

        for domain, components in self.components_data.items():
            if not components:
                continue

            # Créer l'onglet pour ce domaine
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=f"{domain} ({len(components)})")

            # Créer le treeview avec scrollbars
            tree_frame = ttk.Frame(tab_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Treeview
            columns = ("Sélection", "Nom", "Description", "Type", "Domaine", "Fabricant", "SKU Aperçu")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

            # Colonnes
            tree.heading("Sélection", text="✓")
            tree.heading("Nom", text="Nom du Composant")
            tree.heading("Description", text="Description")
            tree.heading("Type", text="Type")
            tree.heading("Domaine", text="Domaine")
            tree.heading("Fabricant", text="Fabricant")
            tree.heading("SKU Aperçu", text="SKU qui sera généré")

            # Largeur des colonnes
            tree.column("Sélection", width=50, anchor=tk.CENTER)
            tree.column("Nom", width=180)
            tree.column("Description", width=200)
            tree.column("Type", width=120)
            tree.column("Domaine", width=70, anchor=tk.CENTER)
            tree.column("Fabricant", width=120)
            tree.column("SKU Aperçu", width=200, anchor=tk.CENTER)

            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # Pack scrollbars et tree
            tree.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            tree_frame.grid_columnconfigure(0, weight=1)
            tree_frame.grid_rowconfigure(0, weight=1)

            # Stocker la référence au tree pour ce domaine
            setattr(self, f"tree_{domain.lower()}", tree)

            # Variables pour les checkboxes et remplissage
            domain_vars = {}

            for i, component in enumerate(components):
                item_id = f"{domain}_{i}"

                # Générer un aperçu du SKU
                try:
                    sku_preview = self.sku_generator.generate_sku(component)
                except Exception:
                    sku_preview = "❌ Erreur"

                # Variable de checkbox (cochée par défaut)
                var = tk.BooleanVar(value=True)
                domain_vars[item_id] = var

                # Insérer dans le treeview
                tree.insert("", tk.END, iid=item_id, values=(
                    "✓",  # Sélection
                    component.name or "N/A",
                    component.description or "N/A",
                    component.component_type or "N/A",
                    component.domain,
                    component.manufacturer or "N/A",
                    sku_preview
                ))

                # Marquer la ligne comme sélectionnée
                tree.set(item_id, "Sélection", "✓")

            # Stocker les variables pour ce domaine
            self.component_vars[domain] = domain_vars

            # Bind pour les clics (corriger le problème de sélection)
            tree.bind("<Button-1>", lambda e, d=domain: self.on_tree_click(e, d))
            tree.bind("<Double-1>", lambda e, d=domain: self.show_component_details(d, e))

        self.update_stats()

    def on_tree_click(self, event, domain):
        """Gérer les clics sur le treeview"""
        tree = getattr(self, f"tree_{domain.lower()}")

        # Identifier l'élément cliqué
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if item and item in self.component_vars[domain]:
            # Toggle la sélection
            current_value = self.component_vars[domain][item].get()
            new_value = not current_value
            self.component_vars[domain][item].set(new_value)

            # Mettre à jour l'affichage
            if new_value:
                tree.set(item, "Sélection", "✓")
                tree.item(item, tags=())
            else:
                tree.set(item, "Sélection", "❌")
                tree.item(item, tags=("deselected",))
                tree.tag_configure("deselected", background="#f0f0f0", foreground="#666666")

            self.update_stats()

            # Empêcher la sélection par défaut du treeview
            return "break"

    def toggle_selection(self, item_id):
        """Basculer la sélection d'un composant (méthode héritée pour compatibilité)"""
        domain = item_id.split("_")[0]

        if item_id in self.component_vars[domain]:
            current_value = self.component_vars[domain][item_id].get()
            new_value = not current_value
            self.component_vars[domain][item_id].set(new_value)

            # Mettre à jour l'affichage
            tree = getattr(self, f"tree_{domain.lower()}")
            tree.set(item_id, "Sélection", "✓" if new_value else "❌")

            # Changer la couleur de fond
            if new_value:
                tree.item(item_id, tags=())
            else:
                tree.item(item_id, tags=("deselected",))
                tree.tag_configure("deselected", background="#f0f0f0", foreground="#666666")

            self.update_stats()

    def select_all(self):
        """Sélectionner tous les composants"""
        for domain, domain_vars in self.component_vars.items():
            tree = getattr(self, f"tree_{domain.lower()}")
            for item_id, var in domain_vars.items():
                var.set(True)
                tree.set(item_id, "Sélection", "✓")
                tree.item(item_id, tags=())
        self.update_stats()

    def deselect_all(self):
        """Désélectionner tous les composants"""
        for domain, domain_vars in self.component_vars.items():
            tree = getattr(self, f"tree_{domain.lower()}")
            for item_id, var in domain_vars.items():
                var.set(False)
                tree.set(item_id, "Sélection", "❌")
                tree.item(item_id, tags=("deselected",))
                tree.tag_configure("deselected", background="#f0f0f0", foreground="#666666")
        self.update_stats()

    def update_stats(self):
        """Mettre à jour les statistiques"""
        total_components = 0
        selected_components = 0

        stats_by_domain = {}

        for domain, domain_vars in self.component_vars.items():
            domain_total = len(domain_vars)
            domain_selected = sum(var.get() for var in domain_vars.values())

            total_components += domain_total
            selected_components += domain_selected
            stats_by_domain[domain] = (domain_selected, domain_total)

        # Créer le texte des statistiques
        stats_text = f"Total: {selected_components}/{total_components} composants sélectionnés"

        for domain, (selected, total) in stats_by_domain.items():
            stats_text += f" | {domain}: {selected}/{total}"

        self.stats_label.config(text=stats_text)

    def show_component_details(self, domain, event):
        """Afficher les détails d'un composant"""
        tree = getattr(self, f"tree_{domain.lower()}")
        selection = tree.selection()

        if selection:
            item_id = selection[0]
            idx = int(item_id.split("_")[1])
            component = self.components_data[domain][idx]

            # Fenêtre de détails
            detail_window = tk.Toplevel(self.window)
            detail_window.title("Détails du Composant")
            detail_window.geometry("500x400")
            detail_window.transient(self.window)

            # Contenu
            text_widget = tk.Text(detail_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)

            details = f"""
🔧 DÉTAILS DU COMPOSANT

Nom: {component.name or 'N/A'}
Description: {component.description or 'N/A'}
Domaine: {component.domain}
Type: {component.component_type or 'N/A'}
Route: {component.route or 'Automatique'}
Routing: {component.routing or 'Automatique'}
Fabricant: {component.manufacturer or 'N/A'}
Référence fabricant: {component.manufacturer_part or 'N/A'}
Quantité: {component.quantity or 'N/A'}
Désignateur: {component.designator or 'N/A'}
"""
            text_widget.insert(tk.END, details)
            text_widget.config(state=tk.DISABLED)

    def get_selected_components(self) -> Dict[str, List[Component]]:
        """Obtenir les composants sélectionnés"""
        selected = {}

        for domain, domain_vars in self.component_vars.items():
            selected_list = []

            for item_id, var in domain_vars.items():
                if var.get():  # Si sélectionné
                    idx = int(item_id.split("_")[1])
                    selected_list.append(self.components_data[domain][idx])

            if selected_list:
                selected[domain] = selected_list

        return selected

    def confirm(self):
        """Confirmer la sélection et procéder à la génération"""
        selected = self.get_selected_components()

        # Vérifier qu'au moins un composant est sélectionné
        total_selected = sum(len(components) for components in selected.values())

        if total_selected == 0:
            messagebox.showwarning("Aucun composant sélectionné",
                                 "Veuillez sélectionner au moins un composant pour générer les SKU.")
            return

        # Confirmer l'action
        message = f"Générer les SKU pour {total_selected} composants sélectionnés ?"
        if messagebox.askyesno("Confirmation", message):
            # Fermer la fenêtre et exécuter le callback
            self.window.destroy()
            if self.callback:
                self.callback(selected)

    def cancel(self):
        """Annuler la validation"""
        if messagebox.askyesno("Annuler", "Êtes-vous sûr de vouloir annuler ?"):
            self.window.destroy()
