# -*- coding: utf-8 -*-

from openerp import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def recompute_line_amount(self):
        for line in self:
            line.on_change_unit_amount(
                self._cr,
                self._uid,
                line.id,
                line.product_id.id,
                line.unit_amount,
                line.company_id.id,
                line.product_uom_id.id,
                line.journal_id.id
            )
