# -*- coding: utf-8 -*-

from openerp.osv import osv


class StockMove(osv.osv):
    _inherit = "stock.move"

    def action_confirm(self, cr, uid, ids, context=None):
        res = super(StockMove, self).action_confirm(cr, uid, ids, context=context)

        move_obj = self.pool.get('stock.move')
        magento_prod_obj = self.pool.get('magento.product')
        magento_tmpl_obj = self.pool.get('magento.product.template')

        moves = move_obj.browse(cr, uid, ids, context=context)
        product_ids = moves.mapped('product_id')
        template_ids = moves.mapped('product_tmpl_id')

        magento_prod_ids = magento_prod_obj.search(cr, uid, [('oe_product_id', 'in', product_ids.ids)], context=context)
        magento_tmpl_ids = magento_tmpl_obj.search(cr, uid, [('erp_template_id', 'in', template_ids.ids)], context=context)

        magento_prod_obj.write(cr, uid, magento_prod_ids, {'need_qty_sync': True}, context=context)
        magento_tmpl_obj.write(cr, uid, magento_tmpl_ids, {'need_qty_sync': True}, context=context)

        return res
