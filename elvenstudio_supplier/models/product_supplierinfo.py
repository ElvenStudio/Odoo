# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


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

    supplier_pricelist_import_id = fields.Many2one('product.pricelist.import', 'id')

    @api.multi
    def product_has_available_qty(self):
        if self:
            for supplier in self:
                if supplier.available_qty > 0.0:
                    return True
        return False

    @api.multi
    def get_supplier_qty(self, index=0):
        qty = 0.0
        if self and len(self) > index:
            qty = self[index].available_qty
        return qty

    @api.multi
    def get_supplier_price(self, supplier_index=0, pricelist_index=0):
        price = 0.0
        if self and len(self) > supplier_index:
            if self[supplier_index].pricelist_ids and len(self[supplier_index].pricelist_ids) > pricelist_index:
                price = self[supplier_index].pricelist_ids[pricelist_index].price
        return price

    @api.multi
    def get_total_supplier_qty(self):
        qty = 0.0
        if self:
            for supplier in self:
                qty += supplier.available_qty
        return qty

    @api.one
    def _compute_condensed_pricelist(self):
        to_text = _("to")
        supplier_pricelist = ''

        for pricelist in self.pricelist_ids:
            supplier_pricelist += ("\n" if supplier_pricelist != '' else '')
            supplier_pricelist += 'Min ' + str(pricelist.min_quantity) + ' ' + to_text + ' ' + str(pricelist.price)

        self.supplier_pricelist_condensed = supplier_pricelist

    @api.model
    def create(self, values):
        update_mto_route = True
        if 'update_mto_route' in values:
            update_mto_route = values['update_mto_route']
            values.pop('update_mto_route')

        sort_product_suppliers = True
        if 'sort_suppliers' in values:
            sort_product_suppliers = values['sort_suppliers']
            values.pop('sort_suppliers')

        supplier = super(ProductSupplierInfo, self).create(values)

        if update_mto_route:
            supplier.product_tmpl_id.update_mto_route()

        if sort_product_suppliers:
            supplier.product_tmpl_id.sort_suppliers()

        return supplier

    @api.multi
    def write(self, values):
        sort_product_suppliers = True
        if 'sort_suppliers' in values:
            sort_product_suppliers = values['sort_suppliers']
            values.pop('sort_suppliers')

        result = super(ProductSupplierInfo, self).write(values)

        if sort_product_suppliers:
            # Aggiorno l'ordine dei fornitori sui prodotti coinvolti,
            # perchè potrebbe essdere cambiato qualcosa
            product_template_obj = self.env['product.template']
            products = product_template_obj.search([('supplier_ids', 'in', self.ids)])
            products.sort_suppliers()

        return result

    @api.multi
    def unlink(self):
        # Aggiorna le regole mto solo ai prodotti coinvolti
        # Aggiorna l'ordine dei fornitori solo ai prodotti coinvolti
        product_template_obj = self.env['product.template']
        products = product_template_obj.search([('supplier_ids', 'in', self.ids)])

        super(ProductSupplierInfo, self).unlink()
        products.update_mto_route()
        products.sort_suppliers()
