# -*- coding: utf-8 -*-

from openerp import models, fields


class PriceListPartnerInfo(models.Model):
    _inherit = "pricelist.partnerinfo"

    suppinfo_id = fields.Many2one(comodel_name='product.supplierinfo', inverse_name='pricelist_ids')
    available_qty = fields.Float(related='suppinfo_id.available_qty', readonly=True, copy=False)

