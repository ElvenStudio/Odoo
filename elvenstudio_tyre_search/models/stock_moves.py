# -*- coding: utf-8 -*-

from openerp import models, fields


class StockMoves(models.Model):
    _inherit = "stock.move"
    product_measure = fields.Char(
        string="Misura",
        related="product_tmpl_id.measure",
        index=True, store=True
    )

    product_compact_measure = fields.Char(
        string="Misura",
        related="product_tmpl_id.compact_measure",
        index=True, store=True
    )

