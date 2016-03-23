# -*- coding: utf-8 -*-

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        # invoices_info structure: {new_invoice_id: [old_invoice_ids]}
        invoices_info = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)

        map(
            lambda merged_invoice_id:
                self.env['stock.picking'].search(
                    # find all stock.picking related to the old invoices
                    [('invoice_id', 'in', invoices_info[merged_invoice_id])]
                    # and set for all the new mereged_invoice_id
                ).write({'invoice_id': merged_invoice_id}),
            invoices_info
        )

        return invoices_info
