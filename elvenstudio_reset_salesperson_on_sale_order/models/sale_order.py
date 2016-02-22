# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def reset_salesperson_from_customer(self):
        for sale_order in self:
            sale_order.write({
                'user_id': sale_order.partner_id.user_id.id,
                'section_id': sale_order.partner_id.section_id.id
            })
            for order_line in sale_order.order_line:
                if order_line.invoiced:
                    raise Warning(_("Cannot reset agents and salesperson of sale order lines already invoiced!"))
                elif not order_line.commission_free:
                    order_line.write({'agents': [(5, False, False)]})
                    order_line.write({
                        'agents': order_line.with_context(partner_id=sale_order.partner_id.id)._default_agents()
                    })
