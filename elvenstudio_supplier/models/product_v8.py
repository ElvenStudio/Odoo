# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductV8(models.Model):
    _inherit = "product.template"

    supplier_qty = fields.Float(
        compute='_get_supplier_available',
        digits=dp.get_precision('Product Unit of Measure'),
        store=True
    )

    @api.one
    @api.depends('supplier_ids.available_qty')
    def _get_supplier_available(self):
        self.supplier_qty = self.supplier_ids.get_total_supplier_qty()
