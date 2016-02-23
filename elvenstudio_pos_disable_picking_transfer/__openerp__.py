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

{'name': 'Disable POS picking auto transfer',
 'license': 'AGPL-3',
 'version': '0.1.0',
 'category': 'Point of Sales',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Disable stock picking auto-transfer on POS",
 'description': """
Disable Point of Sale Stock picking auto transfer
==============================================================

This module disable the auto transfer of the stock picking when a POS order is validated.
To disable the auto transfer, a boolean field is added in the pos config.
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png', ],

 'depends': [
     'point_of_sale',
 ],

 'data': [
     'views/point_of_sale_view.xml',
 ],

 'installable': True,
 'application': False,
 }
