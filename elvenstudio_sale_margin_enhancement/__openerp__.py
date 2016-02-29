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

{'name': 'Sale Margin Enhancement',
 'license': 'AGPL-3',
 'version': '0.1.0',
 'category': 'Sales & Purchases',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Sale margin module Enhanced",
 'description': """
Sale Margin Enhancement
==============================================================

This module extends odoo sale_margin adding this functionalities:
 - get sale order line purchase price from pricelist base cost price;
 - compute margin using product_uom_qty instead of product_uos_qty;
 - add a bulk action to recalculate all sale order margin selected in tree view.
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png',],

 'depends': [
     'sale_margin'
 ],

 'data': [
     'views/sale_order_view.xml',
 ],

 'installable': True,
 'application': False,
 }
