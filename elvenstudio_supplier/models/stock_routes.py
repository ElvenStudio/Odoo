# -*- coding: utf-8 -*-

from openerp import models, fields


class SupplierStockLocationRoute(models.Model):
    _name = 'supplier.stock.location.routes'

    route = fields.Many2one('stock.location.route')
    active = fields.Boolean('Active')

