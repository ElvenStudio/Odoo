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
 'name': 'Supplier Pricelist Management',
 'license': 'AGPL-3',
 'version': '0.0.2',
 'category': 'Purchase',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Import and add supplier pricelist to product",
 'description': """
Improved Supplier pricelist manamegent
==============================================================

This module extends the supplier pricelist with this functionality:
 - Adds for each supplier of a product, the maximum buyable quantity
 - Shows in product kanban view the main supplier quantity and the main supplier price
 - Automatically sort the product supplier's by best price whom has buyable quantity
 - Adds a new menu for importing pricelist and logs OK/KO imported lines

Usage:
------
In Configuration -> Wharehouse new tab "supplier" will be added.
Make sure to select the right MTO rule to use when procurement will be created.

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
     'views/res_config_view.xml',
     'security/ir.model.access.csv'
 ],

 'installable': True,
 'application': False,
 }
