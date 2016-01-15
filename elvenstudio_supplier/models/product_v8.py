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
    def update_mto_route(self):
        settings_obj = self.env['stock.config.settings'].search([('mto_route', '!=', 0)], limit=1, order="id DESC")
        if settings_obj and settings_obj.mto_route.id:
            _route_id = settings_obj.mto_route.id
            for product in self:
                if _route_id in product.route_ids.ids and not product.supplier_ids.ids:
                    # rimuovo l'mto
                    product.write({'route_ids': [(3, _route_id)], 'update_mto_route': True})
                elif _route_id not in product.route_ids.ids and product.supplier_ids.ids:
                    # aggiungo l'mto
                    product.write({'route_ids': [(4, _route_id)], 'update_mto_route': True})

    @api.multi
    def write(self, values):
        result = super(ProductV8, self).write(values)
        if 'update_mto_route' not in values:
            self.update_mto_route()
        return result
