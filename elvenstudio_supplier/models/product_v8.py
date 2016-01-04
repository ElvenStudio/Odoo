# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductV8(models.Model):
    _inherit = "product.template"

    supplier_qty = fields.Float(
        compute='_get_supplier_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        store=True
    )

    supplier_price = fields.Float(
        compute='_get_supplier_price',
        store=True
    )

    @api.one
    @api.depends('supplier_ids.available_qty')
    def _get_supplier_qty(self):
        self.supplier_qty = self.supplier_ids.get_supplier_qty()

    @api.one
    @api.depends('supplier_ids.pricelist_ids.price')
    def _get_supplier_price(self):
        self.supplier_price = self.supplier_ids.get_supplier_price()
