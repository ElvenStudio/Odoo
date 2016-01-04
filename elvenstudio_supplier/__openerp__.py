# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: ElvenStudio
#    Copyright 2015 elvenstudio.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
 'name': 'Gestione dei fornitori',
 'version': '0.0.2',
 'category': 'Customization',
 'description': """
    Estende le funzionalità associate ai fornitori di un prodotto con le seguenti migliorie:
     - Definisce per ogni fornitore di un prodotto, le quantità massime disponibili
     - Riordina automaticamente la lista dei fornitori di un prodotto in base al miglior prezzo
     - Permette di importare un listino fornitori da un apposito menù
     - TODO: gestione dei PO
     - TODO: importazione dei fornitori in batch
     - TODO: creazione report e pivot

==============================================================
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png'],

 'depends': [
     'elvenstudio_control_panel',
     'product',
     'purchase',
     'stock',
 ],

 'data': [
     'wizard/import_price_file_view.xml',
     'views/product_supplierinfo_view.xml',
     'views/product_view.xml',
     'views/product_pricelist_import_line_view.xml',
     'views/product_pricelist_import_view.xml',
     'security/ir.model.access.csv'
 ],

 'installable': True,
 'application': False,
 }
