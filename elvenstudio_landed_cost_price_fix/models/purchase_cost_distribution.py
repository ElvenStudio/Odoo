# -*- coding: utf-8 -*-

from openerp import models


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
