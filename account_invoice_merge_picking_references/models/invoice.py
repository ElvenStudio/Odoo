# -*- coding: utf-8 -*-

from openerp import models, api
import itertools


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        invoices_info = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)

        map(
            lambda merged_invoice_id:
                self.browse(merged_invoice_id).write({
                    'picking_ids':
                        list(
                            set(
                                self.browse(merged_invoice_id).picking_ids.ids
                                +
                                list(
                                    itertools.chain.from_iterable(
                                        map(
                                            lambda old_invoice_id:
                                                self.browse(old_invoice_id).picking_ids.ids,
                                            invoices_info[merged_invoice_id]
                                        )
                                    )
                                )
                            )
                        )
                }),
            invoices_info
        )

        return invoices_info
