# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging
_log = logging.getLogger(__name__)


class MagentoProductTemplate(models.Model):
    _inherit = "magento.product.template"

    need_qty_sync = fields.Boolean(compute="_get_qty_sync", readonly=True, store=True, default=False)
    need_price_sync = fields.Boolean(compute="_get_price_sync", readonly=True, store=True, default=False)

    @api.multi
    @api.depends('template_name.qty_available',
                 'template_name.incoming_qty',
                 'template_name.outgoing_qty',
                 'template_name.virtual_available')
    def _get_qty_sync(self):
        for product in self:
            product.need_qty_sync = True

    @api.multi
    @api.depends('template_name.standard_price')
    def _get_price_sync(self):
        for product in self:
            product.need_price_sync = True

    @api.multi
    def build_qty_data(self):
        return map(
            lambda p:
            [
                'product_stock.update',
                [
                    p.mage_product_id,
                    {
                        'qty': p.template_name.virtual_available,
                        'is_in_stock': 1 if p.template_name.virtual_available > 0 else 0
                    }
                ]
            ],
            self.filtered(lambda p: p.need_qty_sync)
        )

    @api.multi
    def build_price_data(self):
        return map(
            lambda p:
            [
                'product.update',
                [
                    p.mage_product_id,
                    {
                        'price': p.list_price
                    }
                ]
            ],
            self.filtered(lambda p: p.need_price_sync)
        )

    @api.multi
    def sync_inventory_to_magento(self, sync_qty=True, sync_price=True):
        data = []

        if sync_qty:
            qty_data = self.build_qty_data()
            data.extend(qty_data) if qty_data else None

        if sync_price:
            price_data = self.build_price_data()
            data.extend(price_data) if price_data else None

        self.env['magento.synchronization'].sync_to_magento(data)

        sync_result = {}

        if sync_qty:
            sync_result['need_qty_sync'] = False

        if sync_price:
            sync_result['need_price_sync'] = False

        self.write(sync_result)


class MagentoProduct(models.Model):
    _inherit = "magento.product"

    need_qty_sync = fields.Boolean(compute="_get_qty_sync", readonly=True, store=True, default=False)
    need_price_sync = fields.Boolean(compute="_get_price_sync", readonly=True, store=True, default=False)

    @api.multi
    @api.depends('pro_name.qty_available',
                 'pro_name.incoming_qty',
                 'pro_name.outgoing_qty',
                 'pro_name.virtual_available')
    def _get_qty_sync(self):
        for product in self:
            product.need_qty_sync = True

    @api.multi
    @api.depends('pro_name.standard_price')
    def _get_price_sync(self):
        for product in self:
            product.need_price_sync = True

    @api.multi
    def build_qty_data(self):
        return map(
            lambda p:
            [
                'product_stock.update',
                [
                    p.mag_product_id,
                    {
                        'qty': p.pro_name.virtual_available,
                        'is_in_stock': 1 if p.pro_name.virtual_available > 0 else 0
                    }
                ]
            ],
            self.filtered(lambda p: p.need_qty_sync)
        )

    @api.multi
    def build_price_data(self, pricelist_id=None):
        return map(
            lambda p:
            [
                'product.update',
                [
                    p.mag_product_id,
                    {
                        'price': p.pro_name.lst_price if not pricelist_id else p.pro_name.with_context(
                            pricelist=pricelist_id).price
                    }
                ]
            ],
            self.filtered(lambda p: p.need_price_sync)
        )

    @api.multi
    def sync_inventory_to_magento(self, sync_qty=True, sync_price=True):
        pricelist_id = self.env['magento.configure'].get_active_pricelist_id()

        data = []

        if sync_qty:
            qty_data = self.build_qty_data()
            data.extend(qty_data) if qty_data else None

        if sync_price:
            price_data = self.build_price_data(pricelist_id=pricelist_id.id if pricelist_id else None)
            data.extend(price_data) if price_data else None

        self.env['magento.synchronization'].sync_to_magento(data)

        sync_result = {}

        if sync_qty:
            sync_result['need_qty_sync'] = False

        if sync_price:
            sync_result['need_price_sync'] = False

        self.write(sync_result)
