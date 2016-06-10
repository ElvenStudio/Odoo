# -*- coding: utf-8 -*-

from openerp import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(StockMove, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        res['purchase_price'] = move.product_id.cost_price or move.product_id.standard_price or 0.0
        return res
