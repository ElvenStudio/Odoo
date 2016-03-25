# -*- coding: utf-8 -*-

from openerp import models, api


class PurchaseCostDistribution(models.Model):
    _inherit = "purchase.cost.distribution"

    def _product_price_update(self, move, new_price):
        super(PurchaseCostDistribution, self)._product_price_update(move, new_price)

        if (move.location_id.usage == 'supplier' and
                move.product_id.cost_method == 'average'):
            product = move.product_id
            # Write the cost price, as SUPERUSER_ID, because a
            # warehouse manager may not have the right to write on products
            product.sudo().write({'cost_price': product.product_tmpl_id.standard_price})

    @api.one
    def action_force_product_previous_cost(self):
        res = super(PurchaseCostDistribution, self).action_force_product_previous_cost()
        if self.cost_update_type == 'direct':
            for line in self.cost_lines:
                line.product_id.sudo().write({'cost_price': line.product_standard_price_old})
        return res

    @api.one
    def action_force_new_cost(self):
        res = super(PurchaseCostDistribution, self).action_force_new_cost()
        if self.cost_update_type == 'direct':
            for line in self.cost_lines:
                line.product_id.sudo().write({'cost_price': line.standard_price_new})
        return res

    @api.one
    def action_force_previous_cost(self):
        res = super(PurchaseCostDistribution, self).action_force_previous_cost()
        if self.cost_update_type == 'direct':
            for line in self.cost_lines:
                line.product_id.sudo().write({'cost_price': line.standard_price_old})
        return res
