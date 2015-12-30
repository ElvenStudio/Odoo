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
 'version': '0.0.1',
 'category': 'Customization',
 'description': """
    Estende le funzionalità associate ai fornitori di un prodotto con le seguenti migliorie:
     - Imposta automaticamente il flag "Può essere venduto" a True quando un prodotto è in magazzino
       o esiste almeno un fornitore con quantità disponibile.
     - Definisce per ogni fornitore di un prodotto, le quantità massime disponibili
     - TODO: gestione dei PO e scelta del miglior fornitore
     - TODO: importazione dei fornitori in batch e ordinamento per miglior fornitore

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
