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

{'name': 'Merge stock picking references while merging invoices.',
 'license': 'AGPL-3',
 'version': '0.1.0',
 'category': 'Account',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Merge stock picking references",
 'description': """
Merge stock picking references while merging invoices.
==============================================================
This module extends the invoice merge module,
saving the stock picking references from source invoices to the merged invoice.

This module is a glue code for the modules:
- account_invoice_merge
- stock_picking_invoice_link
    """,
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': ['images/elvenstudio.png', ],

 'depends': [
     'account_invoice_merge',
     'stock_picking_invoice_link',
 ],

 'data': [],

 'installable': True,
 'application': False,
 }
