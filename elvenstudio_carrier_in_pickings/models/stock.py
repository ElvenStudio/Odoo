# -*- coding: utf-8 -*-

from openerp.osv import osv


class StockMove(osv.osv):
    _inherit = 'stock.move'

    def action_confirm(self, cr, uid, ids, context=None):
        res = super(StockMove, self).action_confirm(cr, uid, ids, context=context)

        order_to_check = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.procurement_id and \
                    move.procurement_id.sale_line_id and \
                    move.procurement_id.sale_line_id.order_id.carrier_id:
                order_to_check.add(move.procurement_id.sale_line_id.order_id)

        pick_obj = self.pool.get("stock.picking")
        for order in order_to_check:
            if order.picking_ids:
                pick_obj.write(cr, uid, order.picking_ids.ids, {'carrier_id': order.carrier_id.id}, context=context)

        return res
