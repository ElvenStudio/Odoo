# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
# import logging

# _logger = logging.getLogger(__name__)


class ProductV7(osv.osv):
    _inherit = "product.template"
"""
    def _get_sale_ok(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)

        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.virtual_available > 0.0 or obj.supplier_ids.product_has_available_qty()

        # _logger.warning("_get_sale_ok " + str(result) + " " + str(ids))
        return result

    _columns = {
        # TODO: Da valutare se funziona anche quando arriva un'ordine
        'sale_ok': fields.function(_get_sale_ok, type='boolean', store=True)
    }
"""