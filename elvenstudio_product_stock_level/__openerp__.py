# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: ElvenStudio
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
   'name': 'Product stock level',
   'version': '0.1.0',
   'category': 'Customization',
   'description': 'Product stock level',
   'author': "ElvenStudio",
   'license': 'AGPL-3',
   'website': 'http://www.elvenstudio.it',
   'images': ['images/elvenstudio.png',],

   'depends': [
       'product',
       'stock',
       'sale',
   ],

   'data': [
       'views/product_view.xml',
       'views/sale_order.xml',
       'views/sale_order_line.xml',
       'init_data.xml'
   ],

   'installable': False,
   'application': False,
 }
