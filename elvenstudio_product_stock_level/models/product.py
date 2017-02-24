# -*- coding: utf-8 -*-



from openerp import models, fields, api
import logging
_log = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.product"

    stocklevel_ids = fields.One2many(
        comodel_name='product.stocklevel',
        inverse_name='product_id'
    )

    stocklevel_flat = fields.Text(
        string='Stocklevel',
        compute='_get_stocklevel_flat'
    )

    @api.multi
    def _get_stocklevel_flat(self):
        for product in self:
            flat = ""
            if product.stocklevel_ids:
                for sl in product.stocklevel_ids:
                    if(sl.immediately_usable_qty > 0 or sl.incoming_qty >0):
                        flat += '<div style="width: 160px">'
                        flat += '<span style="display: inline-block; width: 60px">' + sl.warehouse_id.name + '</span>'
                        flat += '<span style="display: inline-block; width: 50px">V:' + str(sl.immediately_usable_qty) + '</span>'
                        flat += '<span style="display: inline-block; width: 50px">E:' + str(sl.incoming_qty) + '</span>'
                        flat += '</div>'

                    product.stocklevel_flat = flat
