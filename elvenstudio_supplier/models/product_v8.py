# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


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

    @api.multi
    def write(self, values):

        result = super(ProductV8, self).write(values)

        if 'save_route' in values:
            return result

        for product in self:
            if not product.supplier_ids.ids:

                # lo sto per rimuovere, togli l'mts
                settings_obj = self.env['stock.config.settings'].search([], limit=1, order="id DESC")

                if settings_obj.mto_route.id and \
                        (settings_obj.mto_route.id in product.route_ids.ids):
                    # rimuovo l'mto
                    product.write({'route_ids': [(3, settings_obj.mto_route.id)], 'save_route': True})

        return result
