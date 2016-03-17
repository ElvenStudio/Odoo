# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PriceListPartnerInfo(models.Model):
    _inherit = "pricelist.partnerinfo"

    suppinfo_id = fields.Many2one(comodel_name='product.supplierinfo', inverse_name='pricelist_ids')
    available_qty = fields.Float(related='suppinfo_id.available_qty', readonly=True, copy=False)

    @api.model
    def create(self, values):
        sort_product_suppliers = True
        if 'sort_suppliers' in values:
            sort_product_suppliers = values['sort_suppliers']
            values.pop('sort_suppliers')

        pricelist = super(PriceListPartnerInfo, self).create(values)

        if sort_product_suppliers:
            pricelist.suppinfo_id.product_tmpl_id.sort_suppliers()

        return pricelist

    @api.multi
    def write(self, values):
        sort_suppliers = True
        if 'sort_suppliers' in values:
            sort_suppliers = values['sort_suppliers']
            values.pop('sort_suppliers')

        result = super(PriceListPartnerInfo, self).write(values)

        if sort_suppliers:
            # Aggiorno l'ordine dei fornitori sui prodotti coinvolti,
            # perchè potrebbe essdere cambiato qualcosa
            product_to_sort = set()
            for priceline in self:
                product_to_sort.add(priceline.suppinfo_id.product_tmpl_id.id)

            if product_to_sort:
                self.env['product.template'].browse(list(product_to_sort)).sort_suppliers()

        return result

    @api.multi
    def unlink(self):
        # Aggiorno l'ordine dei fornitori sui prodotti coinvolti,
        # perchè potrebbe essdere cambiato qualcosa
        product_to_sort = set()
        for priceline in self:
            product_to_sort.add(priceline.suppinfo_id.product_tmpl_id.id)

        super(PriceListPartnerInfo, self).unlink()

        if product_to_sort:
            self.env['product.template'].browse(list(product_to_sort)).sort_suppliers()
