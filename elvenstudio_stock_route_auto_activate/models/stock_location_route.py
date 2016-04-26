# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_log = logging.getLogger(__name__)


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    auto_activate_route = fields.Boolean(default=False)

    warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        relation='stock_location_route_warehouse_rel',
        column1='stock_location_route_id',
        column2='stock_warehouse_id',
        string='Warehouses to check',
        copy=False,
        help="The list of warehouses where the route must check product availability"
    )

    @api.multi
    def write(self, values):
        result = super(StockLocationRoute, self).write(values)
        if 'auto_activate_route' in values or 'warehouse_ids' in values:
            all_quants = self.env['stock.quant'].search([])
            all_quants._check_product_routes()

        return result
