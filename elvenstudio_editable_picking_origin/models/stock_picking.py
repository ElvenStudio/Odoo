# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


# ----------------------------------------------------------
# Stock Picking
# ----------------------------------------------------------

class StockPicking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'origin': fields.char(
            'Source Document',
            states={'done': [('readonly', False)], 'cancel': [('readonly', True)]},
            help="Reference of the document",
            select=True
        )
    }
