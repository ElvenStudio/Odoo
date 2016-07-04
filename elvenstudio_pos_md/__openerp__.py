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
 'name': 'ElvenStudio POS MD',
 'license': 'AGPL-3',
 'version': '0.0.1',
 'category': 'Customization',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Pos MD Customization",
 'description': """
Point of Sale Customization
===========================
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'depends': ['point_of_sale', 'pos_pricelist'],

 'qweb': ['static/src/xml/pos.xml'],
 'data': [
     'views/point_of_sale.xml',
 ],

 'installable': True,
 'application': False,
 }
