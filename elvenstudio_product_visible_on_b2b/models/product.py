# -*- coding: utf-8 -*-

from openerp import models, fields, _


class Product(models.Model):
    _inherit = "product.template"

    b2b_ok = fields.Boolean(string=_("Selectable on B2B"), default=True)
