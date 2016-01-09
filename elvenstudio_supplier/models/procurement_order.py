# -*- coding: utf-8 -*-

from openerp import models

from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _get_product_supplier(self, cr, uid, procurement, context=None):
        """ returns the cheapest main supplier of the procurement's product given as argument """

        return super(ProcurementOrder, self)._get_product_supplier(cr, uid, procurement, context)

    def _sort_product_supplier(self):
        return None
