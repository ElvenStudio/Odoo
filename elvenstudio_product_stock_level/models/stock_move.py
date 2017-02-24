# -*- coding: utf-8 -*-

from openerp import models


class StockMove(models.Model):
    _inherit = "stock.move"


    def action_done(self, cr, uid, ids, context=None):
        res = super(StockMove, self).action_done(cr, uid, ids, context=context)
        self.recompute_stocklevel(cr, uid, ids, context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        res = super(StockMove, self).action_cancel(cr, uid, ids, context=context)
        self.recompute_stocklevel(cr, uid, ids, context=context)
        return res

    def recompute_stocklevel(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            source_warehouse = move.location_id.get_warehouse(move.location_id)
            destination_warehouse = move.location_dest_id.get_warehouse(move.location_dest_id)

            if source_warehouse == destination_warehouse:
                # the move is on one warahouse, update it only
                self.pool.get('product.stocklevel').update_stocklevel(cr, uid, source_warehouse, move.product_id.id, context=context)

            else:
                # the move is on different warehouses, update both
                self.pool.get('product.stocklevel').update_stocklevel(cr, uid, source_warehouse, move.product_id.id, context=context)
                self.pool.get('product.stocklevel').update_stocklevel(cr, uid, destination_warehouse, move.product_id.id, context=context)
