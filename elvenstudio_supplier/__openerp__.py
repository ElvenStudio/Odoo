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
 'name': 'Supplier Pricelists Management',
 'license': 'AGPL-3',
 'version': '0.0.2',
 'category': 'Purchase',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Import supplier pricelists into products",
 'description': """
Improved Supplier pricelists manamegent
==============================================================

This module extends the supplier pricelists with this functionalities:
 - Adds, for each supplier of a product, the maximum buyable quantity
 - Shows, in product kanban view, the main supplier quantity and the main supplier price
 - Product supplier's with buyable quantity are sorted automatically, the other are put at last.
 - Adds a new menu for importing pricelists and logs OK/KO imported lines
 - Activate and deactivate pricelists automatically, based on start/end date.
 - Select which location routes will be added/removed to the product when a supplier will be added/removed.

Usage:
------
In __Elvenstudio -> Configuration -> Location Routes__ add how many location routes you need to activate
when a supplier will be added to a product.
In __Elvenstudio -> Product Suppliers -> Pricelists__ you can add new pricelists, using a well-formed CSV file
(provided in data/pricelist.csv).


TODO:
-----
  - Batch pricelist import
  - Reports and pivot table for price analisys
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
     'views/supplier_stock_location_route.xml',
     'data/data.xml',
     'security/ir.model.access.csv'
 ],

 'installable': True,
 'application': False,
 }
