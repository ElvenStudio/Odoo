# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.exceptions import MissingError

# import logging

# _logger = logging.getLogger(__name__)


class PurchaseOrderV7(osv.osv):
    _inherit = 'purchase.order'

    def _get_picking_in(self, cr, uid, context=None):
        obj_data = self.pool.get('ir.model.data')
        type_obj = self.pool.get('stock.picking.type')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id

        # Fixed, @moreinfo, Tejas Tank
        pick_type = type_obj.search(cr, uid,
                                    [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)],
                                    context=context)

        pick_type = pick_type[0] if pick_type != [] else False

        if not pick_type:
            pick_type = type_obj.search(cr, uid, [('code', '=', 'incoming')], context=context)
            pick_type = pick_type[0] if pick_type != [] else False

        if not pick_type:
            raise osv.except_osv(_('Error!'), _("Make sure you have at least an incoming picking type defined"))

        # _logger.warning("elvenstudio _get_picking_in " + str(pick_type))

        return pick_type

    def onchange_picking_type_id(self, cr, uid, ids, picking_type_id, context=None):
        value = {}
        if picking_type_id:
            picktype = self.pool.get("stock.picking.type").browse(cr, uid, picking_type_id, context=context)

            try:
                if picktype.default_location_dest_id:
                    value.update({'location_id': picktype.default_location_dest_id.id,
                                  'related_usage': picktype.default_location_dest_id.usage})
                value.update({'related_location_id': picktype.default_location_dest_id.id})
            except MissingError:
                return self.onchange_picking_type_id(cr, uid, ids, self._get_picking_in(cr, uid, context), context)

        return {'value': value}

    _columns = {
        'picking_type_id': fields.many2one('stock.picking.type', 'Deliver To',
                                           help="This will determine picking type of incoming shipment",
                                           required=True,
                                           states={
                                               'confirmed': [('readonly', True)],
                                               'approved': [('readonly', True)],
                                               'done': [('readonly', True)]
                                           }),
    }

    _defaults = {
        'picking_type_id': _get_picking_in,
    }
