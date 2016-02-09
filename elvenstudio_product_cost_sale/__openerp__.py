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
 'name': 'Product Cost Sale',
 'license': 'AGPL-3',
 'version': '0.1.0',
 'category': 'Sales',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Adds a cost_sale in product",
 'description': """
Relate product stock cost and supplier price.
==============================================================

This module adds a new product cost called cost_sale, that is evaluated as follow:
 * if the product is in stock, the cost is equal to the variant cost price;
 * if the product is not in stock, the price is got from the main supplier.
 * if the context need a quantity Q of the product and the shock has q1 < Q the cost is:
   cost_sale = (q1 * variant_cost_price + (Q - q1) * supplier price ) / Q.

 This new cost_sale can be used in product pricelist as base cost for pricelists.

Usage:
--------------------------------------------------------------
 In Sell -> Configuration -> Pricelist -> Price Type will be able to see a new price type
 called cost sale, usable into the pricelist as base cost.
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png', ],

 'depends': [
     'product',
     'product_supplierinfo_for_customer',
     'product_variant_cost',
 ],

 'data': [
     'data/default.xml',
     'views/product.xml',
 ],

 'installable': True,
 'application': False,
 }
