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
 'name': 'Tyre Product',
 'version': '0.1.0',
 'category': 'Customization',
 'description': """
    Estende il prodotto di odoo con le seguenti funzionalità:
     - Si collega ai prodotti magento
     - Mostra una vista personalizzata sui prodotti associati ad un attribute set valido

    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png',],

 'depends': [
     'product',
     'stock',
     'magento_bridge',
     'mob_product_attribute'
 ],

 'data': [
     'views/product_view.xml',
     'views/stock_view.xml',
     'init_data.xml'
 ],

 'installable': True,
 'application': False,
 }
