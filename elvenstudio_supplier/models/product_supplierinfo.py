# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
# import logging

# _logger = logging.getLogger(__name__)


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

    supplier_pricelist_import_id = fields.One2many('product.pricelist.import', 'name')

    def product_has_available_qty(self):
        if self:
            for supplier in self:
                if supplier.available_qty > 0.0:
                    return True
        return False

    def get_supplier_qty(self, index=0):
        qty = 0.0
        if self and len(self) > index:
            qty = self[index].available_qty
        return qty

    def get_supplier_price(self, supplier_index=0, pricelist_index=0):
        price = 0.0
        if self and len(self) > supplier_index:
            if self[supplier_index].pricelist_ids and len(self[supplier_index].pricelist_ids) > pricelist_index:
                price = self[supplier_index].pricelist_ids[pricelist_index].price
        return price

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

    @api.model
    def create(self, values):
        supplier = super(ProductSupplierInfo, self).create(values)

        supplier.write({'available_qty': supplier.available_qty})
        return supplier

    @api.multi
    def write(self, values):
        # _logger.warning("Supplier to save " + str(values))

        result = super(ProductSupplierInfo, self).write(values)

        # _logger.warning("Saving supplier " + str(result))

        if 'pricelist_ids' in values or 'available_qty' in values:

            price_list_info_obj = self.env['pricelist.partnerinfo']
            sup_info_obj = self.env['product.supplierinfo']

            price_list = price_list_info_obj.search([
                ('suppinfo_id', 'in', self.product_tmpl_id.supplier_ids.ids),
                ('available_qty', '>', 0)],
                order="price ASC")

            i = 1
            ordered_suppliers_ids = []
            suppliers_ids = self.product_tmpl_id.supplier_ids.ids
            for price_line in price_list:
                if price_line.suppinfo_id.id not in ordered_suppliers_ids:
                    ordered_suppliers_ids.append(price_line.suppinfo_id.id)
                    sup_info_obj.browse([price_line.suppinfo_id.id]).write({'sequence': i})
                    i += 1
                if price_line.suppinfo_id.id in suppliers_ids:
                    suppliers_ids.remove(price_line.suppinfo_id.id)

            for dangling_supplier in suppliers_ids:
                sup_info_obj.browse([dangling_supplier]).write({'sequence': i})
                i += 1

        return result
