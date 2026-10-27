from datetime import datetime
import http.server
import json
import os
from pymart.models import PerishableProduct, Product
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
                <p class="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-3 pb-2">Menu Principal</p>
                <a href="#overview" class="flex items-center gap-3.5 px-3 py-2.5 rounded-2xl bg-indigo-50/70 text-indigo-600 font-semibold text-sm transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                    Vue d'ensemble
                </a>
                <a href="#catalog" class="flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 font-medium text-sm transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                    Inventaire
                </a>
                <a href="#reports" class="flex items-center gap-3.5 px-3 py-2.5 rounded-2xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 font-medium text-sm transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    Rapports
                </a>
            </nav>
        </div>

        <div class="p-4 rounded-3xl bg-slate-50 border border-slate-100 flex items-center gap-3">
            <div class="h-9 w-9 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-xs">
                OP
            </div>
            <div class="overflow-hidden">
                <p class="text-xs font-bold text-slate-900 truncate">Opérateur Caisses</p>
                <p class="text-[10px] text-emerald-600 font-semibold flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Connecté
                </p>
            </div>
        </div>
    </aside>

    <main class="flex-1 overflow-y-auto px-6 lg:px-12 py-8 max-w-7xl mx-auto space-y-8">
        <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
                <span class="text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full uppercase tracking-wider">Back-Office Retail</span>
                <h1 class="text-2xl lg:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">Tableau de bord</h1>
                <p class="text-xs sm:text-sm text-slate-400 mt-0.5">Suivi des flux de vente, gestion des stocks et reporting journalier.</p>
            </div>
            <div class="flex items-center gap-3">
                <button onclick="refreshData()" class="p-2.5 rounded-2xl bg-white border border-slate-200/80 text-slate-600 hover:text-slate-900 hover:shadow-sm transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                </button>
                <button onclick="openModal()" class="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs sm:text-sm rounded-2xl shadow-indigo-100 shadow-md transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                    Nouveau produit
                </button>
            </div>
        </header>

        <section id="overview" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
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
                    <span class="text-[11px] text-emerald-600 font-medium">Historique validé</span>
                </div>
                <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                </div>
            </div>
        </section>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <section id="catalog" class="lg:col-span-2 bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-5">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-base font-extrabold text-slate-900">Articles &amp; Niveaux de Stock</h2>
                        <p class="text-xs text-slate-400 mt-0.5">Catalogue synchronisé avec data/products.txt</p>
                    </div>
                    <span id="badge-products-count" class="text-xs font-bold bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
                        0 articles
                    </span>
                </div>

                <div class="overflow-hidden border border-slate-100 rounded-2xl">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="px-5 py-3.5">SKU</th>
                                    <th class="px-5 py-3.5">Article</th>
                                    <th class="px-5 py-3.5">Prix</th>
                                    <th class="px-5 py-3.5">Quantité</th>
                                    <th class="px-5 py-3.5">Condition</th>
                                </tr>
                            </thead>
                            <tbody id="products-table" class="divide-y divide-slate-100 text-slate-700">
                                <tr>
                                    <td colspan="5" class="px-5 py-10 text-center text-slate-400 font-medium">Chargement des données...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section id="reports" class="space-y-6">
                <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
                    <div>
                        <h2 class="text-base font-extrabold text-slate-900">Générateur d'activité</h2>
                        <p class="text-xs text-slate-400 mt-0.5">Édition des synthèses avec calendrier et échéances</p>
                    </div>

                    <div class="space-y-3.5 pt-2">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 mb-1">Fréquence</label>
                            <select id="r-type" onchange="toggleReportInput()" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition">
                                <option value="daily">Rapport Journalier</option>
                                <option value="monthly">Rapport Mensuel</option>
                            </select>
                        </div>

                        <div id="wrap-daily-date">
                            <label class="block text-xs font-bold text-slate-500 mb-1">Date cible</label>
                            <input type="date" id="r-date" value="2026-06-30" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition">
                        </div>

                        <div id="wrap-monthly-date" class="hidden">
                            <label class="block text-xs font-bold text-slate-500 mb-1">Mois cible</label>
                            <input type="month" id="r-month" value="2026-06" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition">
                        </div>

                        <button onclick="requestReport()" class="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-2xl shadow-sm transition">
                            Éditer la synthèse
                        </button>
                    </div>
                </div>

                <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-3">
                    <div class="flex items-center justify-between">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Console de sortie</h3>
                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                    </div>
                    <pre id="report-output" class="bg-slate-950 text-emerald-400 font-mono text-[11px] p-4 rounded-2xl overflow-x-auto min-h-[140px] leading-relaxed">Aucun rapport édité pour cette session.</pre>
                </div>
            </section>
        </div>
    </main>

    <div id="modal-product" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm hidden items-center justify-center p-4 z-50">
        <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-slate-100 space-y-6">
            <div class="flex items-center justify-between border-b border-slate-100 pb-4">
                <div>
                    <h3 class="text-lg font-extrabold text-slate-900">Nouvel Article</h3>
                    <p class="text-xs text-slate-400">Ajout d'une référence au stock PyMart</p>
                </div>
                <button onclick="closeModal()" class="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center transition">
                    &times;
                </button>
            </div>

            <form id="form-add-product" onsubmit="submitProduct(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Identifiant SKU</label>
                    <input type="text" id="p-sku" required placeholder="ex. SKU750" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 uppercase focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Désignation</label>
                    <input type="text" id="p-name" required placeholder="ex. Clavier ergonomique" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Prix (€)</label>
                        <input type="number" step="0.01" min="0" id="p-price" required placeholder="49.90" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1">Quantité initiale</label>
                        <input type="number" min="0" id="p-qty" required placeholder="25" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1">Date limite de consommation (facultatif)</label>
                    <input type="date" id="p-expiry" class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500">
                </div>

                <div id="product-msg" class="text-xs font-semibold hidden p-3 rounded-2xl"></div>

                <div class="flex items-center justify-end gap-3 pt-3">
                    <button type="button" onclick="closeModal()" class="px-4 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold text-xs transition">
                        Annuler
                    </button>
                    <button type="submit" class="px-5 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-indigo-100 shadow-md transition">
                        Enregistrer
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function openModal() {
            document.getElementById('modal-product').classList.remove('hidden');
            document.getElementById('modal-product').classList.add('flex');
        }

        function closeModal() {
            document.getElementById('modal-product').classList.remove('flex');
            document.getElementById('modal-product').classList.add('hidden');
            document.getElementById('product-msg').classList.add('hidden');
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

                document.getElementById('stat-products').innerText = data.products.length;
                document.getElementById('badge-products-count').innerText = `${data.products.length} références`;

                const lowStockCount = data.products.filter(p => p.quantity < 10).length;
                document.getElementById('stat-low-stock').innerText = lowStockCount;

                document.getElementById('stat-customers').innerText = data.customers_count;
                document.getElementById('stat-orders').innerText = data.orders_count;

                const tbody = document.getElementById('products-table');
                if (data.products.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="px-5 py-10 text-center text-slate-400 font-medium">Aucun article dans la base.</td></tr>';
                    return;
                }

                tbody.innerHTML = data.products.map(p => {
                    const isLow = p.quantity < 10;
                    const qtyBadge = isLow
                        ? `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-50 text-amber-600 border border-amber-200/60">${p.quantity} unités</span>`
                        : `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700">${p.quantity} unités</span>`;
                    const conditionBadge = p.expiry_date
                        ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-600 border border-rose-100">Exp. ${p.expiry_date}</span>`
                        : `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-50 text-slate-400">Standard</span>`;

                    return `
                        <tr class="hover:bg-slate-50/70 transition">
                            <td class="px-5 py-4 font-mono font-bold text-indigo-600 text-[11px]">${p.sku}</td>
                            <td class="px-5 py-4 font-semibold text-slate-900">${p.name}</td>
                            <td class="px-5 py-4 font-medium">${p.price.toFixed(2)} €</td>
                            <td class="px-5 py-4">${qtyBadge}</td>
                            <td class="px-5 py-4">${conditionBadge}</td>
                        </tr>
                    `;
                }).join('');
            } catch (err) {
                console.error(err);
            }
        }

        async function submitProduct(event) {
            event.preventDefault();
            const msgBox = document.getElementById('product-msg');
            msgBox.className = 'text-xs font-semibold hidden p-3 rounded-2xl';

            const payload = {
                sku: document.getElementById('p-sku').value.trim(),
                name: document.getElementById('p-name').value.trim(),
                price: parseFloat(document.getElementById('p-price').value),
                quantity: parseInt(document.getElementById('p-qty').value, 10),
                expiry_date: document.getElementById('p-expiry').value || null
            };

            try {
                const res = await fetch('/api/products', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (!res.ok) throw new Error(result.error || 'Erreur lors de l\\'ajout');

                msgBox.innerText = 'Article enregistré avec succès dans data/products.txt !';
                msgBox.className = 'text-xs font-semibold block p-3 rounded-2xl bg-emerald-50 text-emerald-700 border border-emerald-100';
                document.getElementById('form-add-product').reset();
                refreshData();
                setTimeout(() => closeModal(), 1400);
            } catch (err) {
                msgBox.innerText = err.message;
                msgBox.className = 'text-xs font-semibold block p-3 rounded-2xl bg-rose-50 text-rose-600 border border-rose-100';
            }
        }

        async function requestReport() {
            const type = document.getElementById('r-type').value;
            const payload = {
                type: type,
                date: document.getElementById('r-date').value,
                month: document.getElementById('r-month').value
            };

            try {
                const res = await fetch('/api/reports', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (!res.ok) throw new Error(result.error || 'Erreur de génération');
                document.getElementById('report-output').innerText = result.content;
            } catch (err) {
                document.getElementById('report-output').innerText = 'Erreur : ' + err.message;
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
    if self.path in ("/", "/index.html"):
      self._send_html(HTML_DASHBOARD)
      return

    if self.path == "/api/data":
      try:
        products = list(parse_products(self.products_path))
        customers = list(parse_customers(self.customers_path))
        orders = list(
            parse_orders(self.orders_path, {p.sku: p for p in products})
        )

        prod_list = []
        for p in products:
          item = {
              "sku": p.sku,
              "name": p.name,
              "price": p.price,
              "quantity": p.quantity,
              "expiry_date": getattr(p, "expiry_date", None),
          }
          prod_list.append(item)

        payload = {
            "products": prod_list,
            "customers_count": len(customers),
            "orders_count": len(orders),
        }
        self._send_json(payload)
      except Exception as err:
        self._send_json({"error": str(err)}, status=500)
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
      except ValueError:
        self._send_json(
            {"error": "Le prix et la quantite doivent etre positifs"},
            status=400,
        )
        return

      existing_products = {p.sku: p for p in parse_products(self.products_path)}
      if sku in existing_products:
        self._send_json({"error": f"Le SKU {sku} existe deja"}, status=409)
        return

      if expiry_date:
        product_line = f"{sku}, {name}, {price:.2f}, {quantity}, {expiry_date}"
      else:
        product_line = f"{sku}, {name}, {price:.2f}, {quantity}"

      with open(self.products_path, "a", encoding="utf-8") as f:
        f.write("\n" + product_line)

      self._send_json({"success": True, "message": "Produit ajoute avec succes"})
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

    self.send_error(404, "Endpoint API introuvable")


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