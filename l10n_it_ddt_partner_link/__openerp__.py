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
 'name': 'DDT Link in partner form view',
 'license': 'AGPL-3',
 'version': '0.0.1',
 'category': 'Sales',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Add a link to the related ddt's in the partner form.",
 'description': """
The module Adds, in the partner form, the link to the related DDT's.
==============================================================
""",
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png'],

 'depends': [
     'l10n_it_ddt',
     'base',
 ],

 'data': [
     'views/res_partner_view.xml',
 ],

 'installable': True,
 'application': False,
 }
