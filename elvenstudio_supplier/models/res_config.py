# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

import logging

_logger = logging.getLogger(__name__)


class StockSupplierConfigSettings(osv.osv_memory):
    _inherit = 'stock.config.settings'

    _columns = {
        'mto_route': fields.many2one('stock.location.route', "Default Route MTO"),
    }

    def set_default_fields(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)
        ir_values.set_default(cr, uid, 'stock.location.route', 'mto_route',
                              config.mto_route and config.mto_route.id or False)
        return True

    def get_default_fields(self, cr, uid, ids, context=None):
        # values = {}
        ir_values = self.pool.get('ir.values')
        # config = self.browse(cr, uid, ids[0], context)
        mto_route = ir_values.get_default(cr, uid, 'stock.location.route', 'mto_route')
        return {'mto_route': mto_route}
