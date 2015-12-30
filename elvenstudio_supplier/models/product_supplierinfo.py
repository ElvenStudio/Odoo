# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    available_qty = fields.Float('Available Quantity',
                                 required=True,
                                 help="The available quantity that can be purchased from this supplier, expressed "
                                      "in the supplier Product Unit of Measure if not empty, in the default "
                                      "unit of measure of the product otherwise.",
                                 digits=dp.get_precision('Product Unit of Measure'))

    last_modified_date = fields.Datetime(default=fields.Datetime.now(),
                                         help="Last date when supplier's available quantity was modified")

    supplier_pricelist_condensed = fields.Char(compute='_compute_condensed_pricelist')

    def product_has_available_qty(self):
        if self:
            for supplier in self:
                if supplier.available_qty > 0.0:
                    return True
        return False

    def get_total_supplier_qty(self):
        qty = 0.0
        if self:
            for supplier in self:
                qty += supplier.available_qty
        return qty

    @api.one
    def _compute_condensed_pricelist(self):
        atleast_text = _("At least")
        at_text = _("at")
        supplier_pricelist = ''

        for pricelist in self.pricelist_ids:
            supplier_pricelist += ("\n" if supplier_pricelist != '' else '') + \
                atleast_text + " " + str(pricelist.min_quantity) + " " + at_text + " " + str(pricelist.price)

        self.supplier_pricelist_condensed = supplier_pricelist
