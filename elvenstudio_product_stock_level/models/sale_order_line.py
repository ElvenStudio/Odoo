# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging
_log = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    stocklevel_ids = fields.One2many(
        comodel_name='product.stocklevel',
        related="product_id.stocklevel_ids"
    )

    stocklevel_flat = fields.Text(
        string='Stocklevel',
        related='product_id.stocklevel_flat'
    )
