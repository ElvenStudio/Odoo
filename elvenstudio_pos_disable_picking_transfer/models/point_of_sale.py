# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _


class PosConfig(osv.osv):
    _inherit = "pos.config"

    _columns = {
        'auto_transfer_picking': fields.boolean(
            'Auto Transfer Picking', help="If enabled, when a POS order is validated, the stock picking will be "
                                          "automatically confirmed and transfered. Otherwise the stock picking "
                                          "will be only confirmed."),
    }

    _defaults = {
        'auto_transfer_picking': True,
    }


class PointOfSaleOrder(osv.osv):
    _inherit = "pos.order"

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')

        for order in self.browse(cr, uid, ids, context=context):
            if all(t == 'service' for t in order.lines.mapped('product_id.type')):
                continue

            if order and order.session_id.config_id.auto_transfer_picking:
                super(PointOfSaleOrder, self).create_picking(cr, uid, ids, context=context)
            else:
                addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
                picking_type = order.picking_type_id
                picking_id = False
                if picking_type:
                    picking_id = picking_obj.create(cr, uid, {
                        'origin': order.name,
                        'partner_id': addr.get('delivery', False),
                        'date_done': order.date_order,
                        'picking_type_id': picking_type.id,
                        'company_id': order.company_id.id,
                        'move_type': 'direct',
                        'note': order.note or "",
                        'invoice_state': 'none',
                    }, context=context)
                    self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
                location_id = order.location_id.id
                if order.partner_id:
                    destination_id = order.partner_id.property_stock_customer.id
                elif picking_type:
                    if not picking_type.default_location_dest_id:
                        raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                    destination_id = picking_type.default_location_dest_id.id
                else:
                    destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']

                move_list = []
                for line in order.lines:
                    if line.product_id and line.product_id.type == 'service':
                        continue

                    move_list.append(move_obj.create(cr, uid, {
                        'name': line.name,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uos': line.product_id.uom_id.id,
                        'picking_id': picking_id,
                        'picking_type_id': picking_type.id,
                        'product_id': line.product_id.id,
                        'product_uos_qty': abs(line.qty),
                        'product_uom_qty': abs(line.qty),
                        'state': 'draft',
                        'location_id': location_id if line.qty >= 0 else destination_id,
                        'location_dest_id': destination_id if line.qty >= 0 else location_id,
                    }, context=context))

                if picking_id:
                    picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                # Do not force assign picking
                #    picking_obj.force_assign(cr, uid, [picking_id], context=context)
                #    picking_obj.action_done(cr, uid, [picking_id], context=context)
                elif move_list:
                    move_obj.action_confirm(cr, uid, move_list, context=context)
                # Do not force assign stock move
                #    move_obj.force_assign(cr, uid, move_list, context=context)
                #    move_obj.action_done(cr, uid, move_list, context=context)

        return True
