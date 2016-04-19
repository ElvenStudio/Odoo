# -*- coding: utf-8 -*-

from openerp import models, api
# import logging

# _log = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def recompute_line_amount(self):
        for line in self:
            res = line.on_change_unit_amount(
                line.product_id.id,
                line.unit_amount,
                line.company_id.id,
                line.product_uom_id.id,
                line.journal_id.id
            )
            # _log.warning(res)
            line.write({'amount': res[0]['value']['amount']})
