# -*- coding: utf-8 -*-

from openerp import models, fields, api
# import logging

# _log = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cost_sale = fields.Float(compute='_get_cost_sale', readonly=True)

    @api.one
    @api.depends('supplier_ids', 'standard_price')
    def _get_cost_sale(self):
        # TODO pricelist by quantity?

        qty = 0
        if 'quantity' in self.env.context:
            qty = self.env.context['quantity']

        if self.immediately_usable_qty > qty:
            # The stock qty is greather than required qty
            # the cost sale is the stock value
            self.cost_sale = self.standard_price

        elif self.immediately_usable_qty > 0 and self.supplier_ids and self.supplier_ids[0].pricelist_ids:
            # The stock qty is not sufficient for the required qty
            # Use the average price
            self.cost_sale = float(self._get_avg_cost_sale(qty, self.supplier_ids[0].pricelist_ids[0].price)[0])
        #    self.cost_sale = 0
        elif self.supplier_ids and self.supplier_ids[0].pricelist_ids:
            # The stock is empty, i can use only the supplier price
            self.cost_sale = self.supplier_ids[0].pricelist_ids[0].price

        else:
            # No supplier price defined, i can use only the standard_price, 0 if is not set
            self.cost_sale = self.standard_price

    @api.one
    def _get_avg_cost_sale(self, qty, supplier_price):
        return (
            self.immediately_usable_qty * self.standard_price +
            (float(qty) - self.immediately_usable_qty) * float(supplier_price)
            ) / float(qty)


class ProductProduct(models.Model):
    _inherit = "product.product"

    cost_sale = fields.Float(compute='_get_cost_sale', readonly=True)

    @api.one
    @api.depends('supplier_ids', 'cost_price')
    def _get_cost_sale(self):
        # TODO pricelist by quantity?

        qty = 0
        if 'quantity' in self.env.context:
            qty = self.env.context['quantity']

        if self.immediately_usable_qty > qty:
            # The stock qty is greather than required qty
            # the cost sale is the stock value
            self.cost_sale = self.cost_price

        elif self.immediately_usable_qty > 0 and self.supplier_ids and self.supplier_ids[0].pricelist_ids:
            # The stock qty is not sufficient for the required qty
            # Use the average price
            self.cost_sale = float(self._get_avg_cost_sale(qty, self.supplier_ids[0].pricelist_ids[0].price)[0])
        #    self.cost_sale = 0
        elif self.supplier_ids and self.supplier_ids[0].pricelist_ids:
            # The stock is empty, i can use only the supplier price
            self.cost_sale = self.supplier_ids[0].pricelist_ids[0].price

        else:
            # No supplier price defined, i can use only the standard_price, 0 if is not set
            self.cost_sale = self.cost_price

    @api.one
    def _get_avg_cost_sale(self, qty, supplier_price):
        return (
            self.immediately_usable_qty * self.cost_price +
            (float(qty) - self.immediately_usable_qty) * float(supplier_price)
            ) / float(qty)
