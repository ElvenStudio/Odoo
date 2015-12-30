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

{'name': 'ElvenStudio Custom Web Theme',
 'version': '0.0.1',
 'category': 'Customization',
 'description': """
    Personalizzazione del tema standard di Odoo
==============================================================
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',
 'images': ['images/elvenstudio.png',
            ],
 'depends': ['web'],
 'data': [
     'template.xml',
 ],
 'css': ['static/src/css/custom.css'],
 'js': ['static/src/js/custom.js'],
 'installable': True,
 'application': False,
 }
