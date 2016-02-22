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

{'name': 'Reset salesperson & agent on sale order',
 'license': 'AGPL-3',
 'version': '0.1.0',
 'category': 'Sales & Purchases',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Add a bulk action on sale order",
 'description': """
Reset salesperson & agents on sale order
==============================================================

Add a bulk action on sale order
------------------------------------
This module extend the sale order view, adding a bulk action that reset:
- sale order salesperson with the customer salesperson;
- sale order salesteam with the customer salesteam;
- order line agents (for product with commission) with the customer agents.
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png',],

 'depends': [
     'sale',
     'sale_commission'
 ],

 'data': [
     'views/sale_view.xml',
 ],

 'installable': True,
 'application': False,
 }
