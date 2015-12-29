# -*- encoding: utf-8 -*-

from openerp import api, models, _
from openerp.exceptions import MissingError
# import logging

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_picking_in(self):
        obj_data = self.env['ir.model.data']
        type_obj = self.env['stock.picking.type']
        user_obj = self.env['res.users']
        company_id = user_obj.browse(self._uid).company_id.id

        # Fixed, @moreinfo, Tejas Tank
        pick_type = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        pick_type = pick_type[0] if pick_type != [] else False

        if not pick_type:
            pick_type = type_obj.search([('code', '=', 'incoming')])
            pick_type = pick_type[0] if pick_type != [] else False

        if not pick_type:
            raise models.except_orm(_('Error!'), _("Make sure you have at least an incoming picking type defined"))

        # _logger.warning("elvenstudio_v8 _get_picking_in " + str(pick_type))

        return pick_type

    @api.model
    def onchange_picking_type_id(self, ids, picking_type_id):
        value = {}
        if picking_type_id:
            picktype = self.env['stock.picking.type']
            picktype = picktype.browse(picking_type_id)

            try:
                if picktype.default_location_dest_id:
                    value.update({'location_id': picktype.default_location_dest_id.id,
                                  'related_usage': picktype.default_location_dest_id.usage})
                value.update({'related_location_id': picktype.default_location_dest_id.id})
            except MissingError:
                return self.onchange_picking_type_id(ids, self._get_picking_in().id)

        return {'value': value}
