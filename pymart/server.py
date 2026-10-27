from datetime import datetime
import http.server
import json
import os
import urllib.parse
from pymart.exceptions import DataValidationError, InsufficientStockError
from pymart.models import Customer, PerishableProduct, Product
from pymart.parsers import parse_customers, parse_orders, parse_products
from pymart.reports import generate_daily_report, generate_monthly_report

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyMart — Workspace</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-[#F8F9FC] text-slate-800 min-h-screen flex antialiased">
    <aside class="w-64 bg-white border-r border-slate-100 flex flex-col justify-between p-6 hidden md:flex shrink-0">
        <div class="space-y-8">
            <div class="flex items-center gap-3 px-2">
                <div class="h-10 w-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-indigo-200 shadow-md">
                    P
                </div>
                <div>
                    <h2 class="text-sm font-extrabold text-slate-900 tracking-tight leading-tight">PyMart Retail</h2>
                    <p class="text-[11px] font-medium text-slate-400">Back-Office Suite</p>
                </div>
            </div>

            <nav class="space-y-1.5">
                <p class="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-3 pb-2">Navigation</p>
                <button onclick="switchTab('tab-products')" id="nav-products" class="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl bg-indigo-50/70 text-indigo-600 font-semibold text-xs transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                    Articles &amp; Stocks
                </button>
                <button onclick="switchTab('tab-customers')" id="nav-customers" class="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 font-medium text-xs transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                    Clients
                </button>
                <button onclick="switchTab('tab-orders')" id="nav-orders" class="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 font-medium text-xs transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    Commandes
                </button>
                <button onclick="switchTab('tab-reports')" id="nav-reports" class="w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 font-medium text-xs transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    Rapports &amp; Audit
                </button>
            </nav>
        </div>

        <div class="space-y-3">
            <button onclick="runAudit()" class="w-full py-2.5 px-3 rounded-2xl border border-indigo-200 bg-indigo-50/50 hover:bg-indigo-50 text-indigo-700 font-semibold text-xs flex items-center justify-center gap-2 transition">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                Auditer les données
            </button>
            <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 flex items-center gap-3">
                <div class="h-8 w-8 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-xs">
                    OP
                </div>
                <div class="overflow-hidden">
                    <p class="text-xs font-bold text-slate-900 truncate">Opérateur Caisses</p>
                    <p class="text-[10px] text-emerald-600 font-semibold flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Session active
                    </p>
                </div>
            </div>
        </div>
    </aside>

    <main class="flex-1 overflow-y-auto px-6 lg:px-12 py-8 max-w-7xl mx-auto space-y-8">
        <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
                <span class="text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full uppercase tracking-wider">Back-Office Retail</span>
                <h1 class="text-2xl lg:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">Tableau de bord</h1>
                <p class="text-xs sm:text-sm text-slate-400 mt-0.5">Pilotage complet des stocks, ventes et conformité des caisses.</p>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
                <button onclick="refreshData()" class="p-2.5 rounded-2xl bg-white border border-slate-200 text-slate-600 hover:text-slate-900 transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                </button>
                <button onclick="openModal('modal-customer')" class="px-3.5 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-2xl transition">
                    + Nouveau client
                </button>
                <button onclick="openModal('modal-order')" class="px-3.5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-2xl shadow-sm transition">
                    + Nouvelle commande
                </button>
                <button onclick="openModal('modal-product')" class="px-3.5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-2xl shadow-sm transition">
                    + Nouveau produit
                </button>
            </div>
        </header>

        <div id="audit-banner" class="hidden p-4 rounded-2xl border text-xs font-semibold flex items-center justify-between">
            <span id="audit-msg"></span>
            <button onclick="document.getElementById('audit-banner').classList.add('hidden')" class="text-slate-400 hover:text-slate-600 text-sm font-bold">&times;</button>
        </div>

        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Références</p>
                    <p id="stat-products" class="text-3xl font-extrabold text-slate-900 mt-1.5">-</p>
                    <span class="text-[11px] text-slate-400 font-medium">Actives en boutique</span>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                </div>
            </div>

            <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold text-amber-500 uppercase tracking-wider">Stock critique</p>
                    <p id="stat-low-stock" class="text-3xl font-extrabold text-amber-500 mt-1.5">-</p>
                    <span class="text-[11px] text-amber-600 font-medium">Moins de 10 unités</span>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                </div>
            </div>

            <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Clients</p>
                    <p id="stat-customers" class="text-3xl font-extrabold text-slate-900 mt-1.5">-</p>
                    <span class="text-[11px] text-slate-400 font-medium">Comptes enregistrés</span>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                </div>
            </div>

            <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center justify-between">
                <div>
                    <p class="text-xs font-bold text-emerald-500 uppercase tracking-wider">Commandes</p>
                    <p id="stat-orders" class="text-3xl font-extrabold text-emerald-600 mt-1.5">-</p>
                    <span class="text-[11px] text-emerald-600 font-medium">Lignes facturées</span>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                </div>
            </div>
        </section>

        <section id="tab-products" class="tab-panel bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
            <div class="flex items-center justify-between">
                <div>
                    <h2 class="text-base font-extrabold text-slate-900">Articles &amp; Niveaux de Stock</h2>
                    <p class="text-xs text-slate-400 mt-0.5">Fichier source : data/products.txt</p>
                </div>
                <span id="badge-products-count" class="text-xs font-bold bg-slate-100 text-slate-600 px-3 py-1 rounded-full">0 références</span>
            </div>
            <div class="overflow-x-auto border border-slate-100 rounded-2xl">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                        <tr>
                            <th class="px-5 py-3.5">SKU</th>
                            <th class="px-5 py-3.5">Désignation</th>
                            <th class="px-5 py-3.5">Prix</th>
                            <th class="px-5 py-3.5">Quantité en stock</th>
                            <th class="px-5 py-3.5">Condition</th>
                        </tr>
                    </thead>
                    <tbody id="products-table" class="divide-y divide-slate-100 text-slate-700">
                        <tr><td colspan="5" class="px-5 py-8 text-center text-slate-400">Chargement...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section id="tab-customers" class="tab-panel hidden bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
            <div class="flex items-center justify-between">
                <div>
                    <h2 class="text-base font-extrabold text-slate-900">Comptes Clients</h2>
                    <p class="text-xs text-slate-400 mt-0.5">Fichier source : data/customers.txt</p>
                </div>
                <span id="badge-customers-count" class="text-xs font-bold bg-slate-100 text-slate-600 px-3 py-1 rounded-full">0 clients</span>
            </div>
            <div class="overflow-x-auto border border-slate-100 rounded-2xl">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                        <tr>
                            <th class="px-5 py-3.5">ID Client</th>
                            <th class="px-5 py-3.5">Nom complet</th>
                            <th class="px-5 py-3.5">E-mail</th>
                            <th class="px-5 py-3.5">Points fidélité</th>
                        </tr>
                    </thead>
                    <tbody id="customers-table" class="divide-y divide-slate-100 text-slate-700">
                        <tr><td colspan="4" class="px-5 py-8 text-center text-slate-400">Chargement...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section id="tab-orders" class="tab-panel hidden bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
            <div class="flex items-center justify-between">
                <div>
                    <h2 class="text-base font-extrabold text-slate-900">Historique des Commandes</h2>
                    <p class="text-xs text-slate-400 mt-0.5">Fichier source : data/orders.txt</p>
                </div>
                <span id="badge-orders-count" class="text-xs font-bold bg-slate-100 text-slate-600 px-3 py-1 rounded-full">0 commandes</span>
            </div>
            <div class="overflow-x-auto border border-slate-100 rounded-2xl">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                        <tr>
                            <th class="px-5 py-3.5">N° Commande</th>
                            <th class="px-5 py-3.5">Date</th>
                            <th class="px-5 py-3.5">Client</th>
                            <th class="px-5 py-3.5">Articles</th>
                            <th class="px-5 py-3.5">Total (€)</th>
                        </tr>
                    </thead>
                    <tbody id="orders-table" class="divide-y divide-slate-100 text-slate-700">
                        <tr><td colspan="5" class="px-5 py-8 text-center text-slate-400">Chargement...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section id="tab-reports" class="tab-panel hidden space-y-8">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
                    <div>
                        <h2 class="text-base font-extrabold text-slate-900">Éditer un Rapport</h2>
                        <p class="text-xs text-slate-400 mt-0.5">Calcul automatique des totaux et échéances</p>
                    </div>

                    <div class="space-y-3.5 pt-2">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 mb-1">Fréquence</label>
                            <select id="r-type" onchange="toggleReportInput()" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none">
                                <option value="daily">Rapport Journalier</option>
                                <option value="monthly">Rapport Mensuel</option>
                            </select>
                        </div>

                        <div id="wrap-daily-date">
                            <label class="block text-xs font-bold text-slate-500 mb-1">Date cible</label>
                            <input type="date" id="r-date" value="2026-06-30" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none">
                        </div>

                        <div id="wrap-monthly-date" class="hidden">
                            <label class="block text-xs font-bold text-slate-500 mb-1">Mois cible</label>
                            <input type="month" id="r-month" value="2026-06" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none">
                        </div>

                        <button onclick="requestReport()" class="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-2xl transition">
                            Générer le rapport
                        </button>
                    </div>
                </div>

                <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
                    <div>
                        <h2 class="text-base font-extrabold text-slate-900">Rapports Enregistrés</h2>
                        <p class="text-xs text-slate-400 mt-0.5">Fichiers dans reports/</p>
                    </div>
                    <div id="reports-file-list" class="space-y-2 max-h-56 overflow-y-auto">
                        <p class="text-xs text-slate-400">Aucun fichier trouvé.</p>
                    </div>
                </div>

                <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-3">
                    <div class="flex items-center justify-between">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Aperçu Fichier</h3>
                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                    </div>
                    <pre id="report-output" class="bg-slate-950 text-emerald-400 font-mono text-[11px] p-4 rounded-2xl overflow-x-auto min-h-[160px] leading-relaxed">Sélectionnez ou générez un rapport pour voir son contenu.</pre>
                </div>
            </div>
        </section>
    </main>

    <div id="modal-product" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-slate-100 space-y-5">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 class="text-lg font-extrabold text-slate-900">Nouvel Article</h3>
                <button onclick="closeModal('modal-product')" class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center">&times;</button>
            </div>
            <form onsubmit="submitProduct(event)" class="space-y-3.5">
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">SKU</label>
                    <input type="text" id="p-sku" required placeholder="SKU500" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold uppercase focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Désignation</label>
                    <input type="text" id="p-name" required placeholder="Clavier USB" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Prix (€)</label>
                        <input type="number" step="0.01" min="0" id="p-price" required placeholder="29.90" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Quantité</label>
                        <input type="number" min="0" id="p-qty" required placeholder="30" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Péremption (optionnel)</label>
                    <input type="date" id="p-expiry" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                </div>
                <div id="product-msg" class="text-xs font-semibold hidden p-3 rounded-2xl"></div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeModal('modal-product')" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-2xl text-xs font-semibold">Annuler</button>
                    <button type="submit" class="px-5 py-2 bg-indigo-600 text-white rounded-2xl text-xs font-semibold">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>

    <div id="modal-customer" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-slate-100 space-y-5">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 class="text-lg font-extrabold text-slate-900">Nouveau Client</h3>
                <button onclick="closeModal('modal-customer')" class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center">&times;</button>
            </div>
            <form onsubmit="submitCustomer(event)" class="space-y-3.5">
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">ID Client</label>
                    <input type="text" id="c-id" required placeholder="CUST010" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold uppercase focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Nom complet</label>
                    <input type="text" id="c-name" required placeholder="Jean Dupont" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Adresse e-mail</label>
                    <input type="email" id="c-email" required placeholder="jean.dupont@example.com" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Points fidélité initiaux</label>
                    <input type="number" min="0" id="c-points" value="0" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                </div>
                <div id="customer-msg" class="text-xs font-semibold hidden p-3 rounded-2xl"></div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeModal('modal-customer')" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-2xl text-xs font-semibold">Annuler</button>
                    <button type="submit" class="px-5 py-2 bg-indigo-600 text-white rounded-2xl text-xs font-semibold">Ajouter le client</button>
                </div>
            </form>
        </div>
    </div>

    <div id="modal-order" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-slate-100 space-y-5">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 class="text-lg font-extrabold text-slate-900">Nouvelle Commande</h3>
                <button onclick="closeModal('modal-order')" class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center">&times;</button>
            </div>
            <form onsubmit="submitOrder(event)" class="space-y-3.5">
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">N° Commande</label>
                    <input type="text" id="o-id" required placeholder="ORD100" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold uppercase focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Client</label>
                    <select id="o-customer" required class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none"></select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Article</label>
                    <select id="o-product" required class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none"></select>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Quantité</label>
                        <input type="number" min="1" id="o-qty" required value="1" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Date</label>
                        <input type="date" id="o-date" required class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold focus:outline-none">
                    </div>
                </div>
                <div id="order-msg" class="text-xs font-semibold hidden p-3 rounded-2xl"></div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeModal('modal-order')" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-2xl text-xs font-semibold">Annuler</button>
                    <button type="submit" class="px-5 py-2 bg-emerald-600 text-white rounded-2xl text-xs font-semibold">Valider la vente</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let cachedData = { products: [], customers: [], orders: [] };

        function switchTab(tabId) {
            document.querySelectorAll('.tab-panel').forEach(el => el.classList.add('hidden'));
            document.getElementById(tabId).classList.remove('hidden');

            const navs = ['nav-products', 'nav-customers', 'nav-orders', 'nav-reports'];
            navs.forEach(id => {
                const btn = document.getElementById(id);
                btn.className = 'w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 font-medium text-xs transition';
            });
            const activeNav = document.getElementById(tabId.replace('tab-', 'nav-'));
            if (activeNav) {
                activeNav.className = 'w-full flex items-center gap-3.5 px-3 py-2.5 rounded-2xl bg-indigo-50/70 text-indigo-600 font-semibold text-xs transition';
            }
        }

        function openModal(id) {
            document.getElementById(id).classList.remove('hidden');
            document.getElementById(id).classList.add('flex');
            if (id === 'modal-order') {
                document.getElementById('o-date').value = new Date().toISOString().split('T')[0];
                populateOrderSelects();
            }
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('flex');
            document.getElementById(id).classList.add('hidden');
        }

        function populateOrderSelects() {
            const custSelect = document.getElementById('o-customer');
            custSelect.innerHTML = cachedData.customers.map(c => `<option value="${c.id}">${c.name} (${c.id})</option>`).join('');

            const prodSelect = document.getElementById('o-product');
            prodSelect.innerHTML = cachedData.products.map(p => `<option value="${p.sku}">${p.name} - ${p.price.toFixed(2)} € (Stock: ${p.quantity})</option>`).join('');
        }

        function toggleReportInput() {
            const type = document.getElementById('r-type').value;
            document.getElementById('wrap-daily-date').classList.toggle('hidden', type !== 'daily');
            document.getElementById('wrap-monthly-date').classList.toggle('hidden', type !== 'monthly');
        }

        async function refreshData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                cachedData = data;

                document.getElementById('stat-products').innerText = data.products.length;
                document.getElementById('badge-products-count').innerText = `${data.products.length} références`;
                document.getElementById('stat-low-stock').innerText = data.products.filter(p => p.quantity < 10).length;
                document.getElementById('stat-customers').innerText = data.customers.length;
                document.getElementById('badge-customers-count').innerText = `${data.customers.length} clients`;
                document.getElementById('stat-orders').innerText = data.orders.length;
                document.getElementById('badge-orders-count').innerText = `${data.orders.length} commandes`;

                const tbodyProd = document.getElementById('products-table');
                tbodyProd.innerHTML = data.products.map(p => {
                    const isLow = p.quantity < 10;
                    const badge = isLow
                        ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-600 border border-amber-200">${p.quantity} unités</span>`
                        : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">${p.quantity} unités</span>`;
                    const cond = p.expiry_date
                        ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-600">Périssable (${p.expiry_date})</span>`
                        : `<span class="text-slate-400 text-[10px]">Standard</span>`;
                    return `<tr class="hover:bg-slate-50/70 transition">
                        <td class="px-5 py-3 font-mono font-bold text-indigo-600">${p.sku}</td>
                        <td class="px-5 py-3 font-semibold text-slate-900">${p.name}</td>
                        <td class="px-5 py-3 font-medium">${p.price.toFixed(2)} €</td>
                        <td class="px-5 py-3">${badge}</td>
                        <td class="px-5 py-3">${cond}</td>
                    </tr>`;
                }).join('') || '<tr><td colspan="5" class="p-4 text-center text-slate-400">Aucun produit</td></tr>';

                const tbodyCust = document.getElementById('customers-table');
                tbodyCust.innerHTML = data.customers.map(c => `
                    <tr class="hover:bg-slate-50/70 transition">
                        <td class="px-5 py-3 font-mono font-bold text-purple-600">${c.id}</td>
                        <td class="px-5 py-3 font-semibold text-slate-900">${c.name}</td>
                        <td class="px-5 py-3 text-slate-500">${c.email}</td>
                        <td class="px-5 py-3 font-semibold text-slate-700">${c.points} pts</td>
                    </tr>
                `).join('') || '<tr><td colspan="4" class="p-4 text-center text-slate-400">Aucun client</td></tr>';

                const tbodyOrders = document.getElementById('orders-table');
                tbodyOrders.innerHTML = data.orders.map(o => `
                    <tr class="hover:bg-slate-50/70 transition">
                        <td class="px-5 py-3 font-mono font-bold text-emerald-600">${o.order_id}</td>
                        <td class="px-5 py-3 text-slate-500">${o.order_date}</td>
                        <td class="px-5 py-3 font-medium text-slate-700">${o.customer_id}</td>
                        <td class="px-5 py-3 text-slate-500">${o.items_count} article(s)</td>
                        <td class="px-5 py-3 font-bold text-slate-900">${o.total.toFixed(2)} €</td>
                    </tr>
                `).join('') || '<tr><td colspan="5" class="p-4 text-center text-slate-400">Aucune commande</td></tr>';

                const reportsList = document.getElementById('reports-file-list');
                if (data.report_files && data.report_files.length > 0) {
                    reportsList.innerHTML = data.report_files.map(f => `
                        <div onclick="viewReport('${f}')" class="p-2.5 rounded-xl border border-slate-100 hover:border-indigo-200 hover:bg-indigo-50/30 cursor-pointer flex items-center justify-between text-xs transition">
                            <span class="font-mono text-slate-700 truncate">${f}</span>
                            <span class="text-indigo-600 font-bold">&rarr;</span>
                        </div>
                    `).join('');
                } else {
                    reportsList.innerHTML = '<p class="text-xs text-slate-400">Aucun rapport généré.</p>';
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function runAudit() {
            const banner = document.getElementById('audit-banner');
            const msg = document.getElementById('audit-msg');
            banner.classList.remove('hidden');

            try {
                const res = await fetch('/api/audit');
                const out = await res.json();
                if (out.valid) {
                    banner.className = 'p-4 rounded-2xl border bg-emerald-50 border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center justify-between';
                    msg.innerText = `Audit validé avec succès : ${out.products} produits, ${out.customers} clients et ${out.orders} commandes conformes sans aucune anomalie.`;
                } else {
                    banner.className = 'p-4 rounded-2xl border bg-rose-50 border-rose-200 text-rose-800 text-xs font-semibold flex items-center justify-between';
                    msg.innerText = `Anomalie détectée lors de l'audit : ${out.error}`;
                }
            } catch (err) {
                banner.className = 'p-4 rounded-2xl border bg-rose-50 border-rose-200 text-rose-800 text-xs font-semibold flex items-center justify-between';
                msg.innerText = 'Erreur technique lors de la vérification des fichiers.';
            }
        }

        async function submitProduct(e) {
            e.preventDefault();
            const msg = document.getElementById('product-msg');
            const payload = {
                sku: document.getElementById('p-sku').value.trim(),
                name: document.getElementById('p-name').value.trim(),
                price: parseFloat(document.getElementById('p-price').value),
                quantity: parseInt(document.getElementById('p-qty').value, 10),
                expiry_date: document.getElementById('p-expiry').value || null
            };

            const res = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const out = await res.json();
            if (!res.ok) {
                msg.className = 'text-xs font-semibold block p-3 rounded-2xl bg-rose-50 text-rose-600';
                msg.innerText = out.error;
            } else {
                msg.className = 'text-xs font-semibold block p-3 rounded-2xl bg-emerald-50 text-emerald-700';
                msg.innerText = 'Article enregistré avec succès.';
                refreshData();
                setTimeout(() => closeModal('modal-product'), 1200);
            }
        }

        async function submitCustomer(e) {
            e.preventDefault();
            const msg = document.getElementById('customer-msg');
            const payload = {
                id: document.getElementById('c-id').value.trim(),
                name: document.getElementById('c-name').value.trim(),
                email: document.getElementById('c-email').value.trim(),
                points: parseInt(document.getElementById('c-points').value, 10) || 0
            };

            const res = await fetch('/api/customers', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const out = await res.json();
            if (!res.ok) {
                msg.className = 'text-xs font-semibold block p-3 rounded-2xl bg-rose-50 text-rose-600';
                msg.innerText = out.error;
            } else {
                msg.className = 'text-xs font-semibold block p-3 rounded-2xl bg-emerald-50 text-emerald-700';
                msg.innerText = 'Client enregistré avec succès.';
                refreshData();
                setTimeout(() => closeModal('modal-customer'), 1200);
            }
        }

        async function submitOrder(e) {
            e.preventDefault();
            const msg = document.getElementById('order-msg');
            const payload = {
                order_id: document.getElementById('o-id').value.trim(),
                customer_id: document.getElementById('o-customer').value,
                sku: document.getElementById('o-product').value,
                quantity: parseInt(document.getElementById('o-qty').value, 10),
                date: document.getElementById('o-date').value
            };

            const res = await fetch('/api/orders', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const out = await res.json();
            if (!res.ok) {
                msg.className = 'text-xs font-semibold block p-3 rounded-2xl bg-rose-50 text-rose-600';
                msg.innerText = out.error;
            } else {
                msg.className = 'text-xs font-semibold block p-3 rounded-2xl bg-emerald-50 text-emerald-700';
                msg.innerText = 'Commande facturée et stock déduit.';
                refreshData();
                setTimeout(() => closeModal('modal-order'), 1200);
            }
        }

        async function requestReport() {
            const type = document.getElementById('r-type').value;
            const payload = {
                type: type,
                date: document.getElementById('r-date').value,
                month: document.getElementById('r-month').value
            };

            const res = await fetch('/api/reports', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const out = await res.json();
            if (res.ok) {
                document.getElementById('report-output').innerText = out.content;
                refreshData();
            } else {
                document.getElementById('report-output').innerText = 'Erreur : ' + out.error;
            }
        }

        async function viewReport(filename) {
            const res = await fetch(`/api/reports/view?file=${encodeURIComponent(filename)}`);
            const out = await res.json();
            if (res.ok) {
                document.getElementById('report-output').innerText = out.content;
            } else {
                document.getElementById('report-output').innerText = out.error;
            }
        }

        window.onload = refreshData;
    </script>
</body>
</html>
"""


class PyMartServerHandler(http.server.BaseHTTPRequestHandler):

  products_path = "data/products.txt"
  customers_path = "data/customers.txt"
  orders_path = "data/orders.txt"
  reports_dir = "reports"

  def _send_json(self, data, status=200):
    content = json.dumps(data).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", str(len(content)))
    self.end_headers()
    self.wfile.write(content)

  def _send_html(self, html_content, status=200):
    content = html_content.encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "text/html; charset=utf-8")
    self.send_header("Content-Length", str(len(content)))
    self.end_headers()
    self.wfile.write(content)

  def do_GET(self):
    parsed_url = urllib.parse.urlparse(self.path)

    if parsed_url.path in ("/", "/index.html"):
      self._send_html(HTML_DASHBOARD)
      return

    if parsed_url.path == "/api/data":
      try:
        products = list(parse_products(self.products_path))
        customers = list(parse_customers(self.customers_path))
        orders = list(
            parse_orders(self.orders_path, {p.sku: p for p in products})
        )

        prod_list = [
            {
                "sku": p.sku,
                "name": p.name,
                "price": p.price,
                "quantity": p.quantity,
                "expiry_date": getattr(p, "expiry_date", None),
            }
            for p in products
        ]

        cust_list = [
            {
                "id": c.customer_id,
                "name": c.name,
                "email": c.email,
                "points": c.loyalty_points,
            }
            for c in customers
        ]

        ord_list = [
            {
                "order_id": o.order_id,
                "customer_id": o.customer_id,
                "order_date": o.order_date,
                "items_count": len(o.items),
                "total": o.total_amount,
            }
            for o in orders
        ]

        report_files = []
        if os.path.exists(self.reports_dir):
          report_files = sorted(
              [
                  f
                  for f in os.listdir(self.reports_dir)
                  if f.startswith("report_") and f.endswith(".txt")
              ],
              reverse=True,
          )

        self._send_json({
            "products": prod_list,
            "customers": cust_list,
            "orders": ord_list,
            "report_files": report_files,
        })
      except Exception as err:
        self._send_json({"error": str(err)}, status=500)
      return

    if parsed_url.path == "/api/audit":
      try:
        prods = list(parse_products(self.products_path))
        custs = list(parse_customers(self.customers_path))
        ords = list(parse_orders(self.orders_path, {p.sku: p for p in prods}))
        self._send_json({
            "valid": True,
            "products": len(prods),
            "customers": len(custs),
            "orders": len(ords),
        })
      except Exception as err:
        self._send_json({"valid": False, "error": str(err)})
      return

    if parsed_url.path == "/api/reports/view":
      query_params = urllib.parse.parse_qs(parsed_url.query)
      filename = query_params.get("file", [""])[0]
      safe_filename = os.path.basename(filename)
      filepath = os.path.join(self.reports_dir, safe_filename)
      if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
          content = f.read()
        self._send_json({"file": safe_filename, "content": content})
      else:
        self._send_json({"error": "Fichier introuvable"}, status=404)
      return

    self.send_error(404, "Page introuvable")

  def do_POST(self):
    content_length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(content_length).decode("utf-8")

    try:
      payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
      self._send_json({"error": "Corps JSON invalide"}, status=400)
      return

    if self.path == "/api/products":
      sku = str(payload.get("sku", "")).strip().upper()
      name = str(payload.get("name", "")).strip()
      price = payload.get("price")
      quantity = payload.get("quantity")
      expiry_date = payload.get("expiry_date")

      if not sku or not name or price is None or quantity is None:
        self._send_json({"error": "Tous les champs sont requis"}, status=400)
        return

      try:
        price = float(price)
        quantity = int(quantity)
        if price < 0 or quantity < 0:
          raise ValueError()
        if expiry_date:
          p = PerishableProduct(sku, name, price, quantity, expiry_date)
        else:
          p = Product(sku, name, price, quantity)
      except Exception as err:
        self._send_json({"error": str(err)}, status=400)
        return

      existing = {p.sku: p for p in parse_products(self.products_path)}
      if sku in existing:
        self._send_json({"error": f"Le SKU {sku} existe deja"}, status=409)
        return

      line = (
          f"{sku}, {name}, {price:.2f}, {quantity}, {expiry_date}"
          if expiry_date
          else f"{sku}, {name}, {price:.2f}, {quantity}"
      )
      with open(self.products_path, "a", encoding="utf-8") as f:
        f.write("\n" + line)
      self._send_json({"success": True})
      return

    if self.path == "/api/customers":
      cust_id = str(payload.get("id", "")).strip().upper()
      name = str(payload.get("name", "")).strip()
      email = str(payload.get("email", "")).strip()
      points = payload.get("points", 0)

      try:
        points = int(points)
        c = Customer(cust_id, name, email, points)
      except Exception as err:
        self._send_json({"error": str(err)}, status=400)
        return

      existing = {c.customer_id: c for c in parse_customers(self.customers_path)}
      if cust_id in existing:
        self._send_json(
            {"error": f"Le client {cust_id} existe deja"}, status=409
        )
        return

      line = f"{cust_id}, {name}, {email}, {points}"
      with open(self.customers_path, "a", encoding="utf-8") as f:
        f.write("\n" + line)
      self._send_json({"success": True})
      return

    if self.path == "/api/orders":
      order_id = str(payload.get("order_id", "")).strip().upper()
      customer_id = str(payload.get("customer_id", "")).strip().upper()
      sku = str(payload.get("sku", "")).strip().upper()
      order_date = str(payload.get("date", "")).strip()
      qty = payload.get("quantity")

      try:
        qty = int(qty)
        if qty <= 0:
          raise ValueError("La quantite doit etre superieure a 0")
      except ValueError as err:
        self._send_json({"error": str(err)}, status=400)
        return

      products = {p.sku: p for p in parse_products(self.products_path)}
      if sku not in products:
        self._send_json({"error": "Produit introuvable"}, status=404)
        return

      product = products[sku]
      if product.quantity < qty:
        self._send_json(
            {
                "error": (
                    f"Stock insuffisant ({product.quantity} disponibles pour"
                    f" {qty} demandes)"
                )
            },
            status=400,
        )
        return

      order_line = f"{order_id}, {customer_id}, {order_date}, {sku}, {qty}"
      with open(self.orders_path, "a", encoding="utf-8") as f:
        f.write("\n" + order_line)

      with open(self.products_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

      new_lines = []
      for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
          new_lines.append(line)
          continue
        parts = [p.strip() for p in stripped.split(",")]
        if parts[0].upper() == sku:
          current_qty = int(parts[3])
          parts[3] = str(current_qty - qty)
          new_lines.append(", ".join(parts) + "\n")
        else:
          new_lines.append(line)

      with open(self.products_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

      self._send_json({"success": True})
      return

    if self.path == "/api/reports":
      report_type = payload.get("type")
      try:
        products = {p.sku: p for p in parse_products(self.products_path)}
        orders = list(parse_orders(self.orders_path, products))

        if report_type == "daily":
          date = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
          path, content = generate_daily_report(orders, date, self.reports_dir)
          self._send_json({"path": path, "content": content})
        elif report_type == "monthly":
          month = payload.get("month") or datetime.now().strftime("%Y-%m")
          path, content = generate_monthly_report(
              orders, month, self.reports_dir
          )
          self._send_json({"path": path, "content": content})
        else:
          self._send_json({"error": "Type de rapport inconnu"}, status=400)
      except Exception as err:
        self._send_json({"error": str(err)}, status=500)
      return

    self.send_error(404, "Endpoint introuvable")


def run_server(
    port=8000,
    products_path="data/products.txt",
    customers_path="data/customers.txt",
    orders_path="data/orders.txt",
    reports_dir="reports",
):
  PyMartServerHandler.products_path = products_path
  PyMartServerHandler.customers_path = customers_path
  PyMartServerHandler.orders_path = orders_path
  PyMartServerHandler.reports_dir = reports_dir

  server_address = ("", port)
  httpd = http.server.HTTPServer(server_address, PyMartServerHandler)
  print(f"Serveur PyMart demarre sur http://localhost:{port}")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print("\nArret du serveur PyMart.")
    httpd.server_close()