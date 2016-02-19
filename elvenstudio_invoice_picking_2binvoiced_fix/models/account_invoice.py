# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def unlink(self):
        for invoice in self:
            picking_names = []
            if invoice.origin:
                if invoice.origin.find(",") >= 0:
                    picking_names = invoice.origin.split(',')
                else:
                    picking_names = [invoice.origin]

            for picking_name in picking_names:
                cond = [('name', '=', picking_name)]
                picking = self.env['stock.picking'].search(cond, limit=1)
                if picking and picking.state != 'cancel' and picking.state != '2binvoiced':
                    raise exceptions.Warning(_('Before deleting invoice should'
                                               ' cancel the picking: %s') % picking_name)

        return super(AccountInvoice, self).unlink()

    @api.multi
    def action_cancel(self):

        # Hold on invoices state before cancel action
        invoices = {key: state for key, state in map(lambda s: (s.id, s.state), self)}
        res = super(AccountInvoice, self).action_cancel()

        # If the super action_cancel does not raise any error
        # can be checked the relative pickings
        for invoice in self:
            # Cant use invoice.state because is already in 'cancel' state
            # if invoice.state not in ['draft', 'proforma', 'proforma2']:
            if invoices[invoice.id] not in ['draft', 'proforma', 'proforma2']:
                picking_names = []
                if invoice.origin:
                    if invoice.origin.find(",") >= 0:
                        picking_names = invoice.origin.split(',')
                    else:
                        picking_names = [invoice.origin]

                for picking_name in picking_names:
                    # Remove any whitespace before search
                    cond = [('name', '=', picking_name.replace(' ', ''))]
                    picking = self.env['stock.picking'].search(cond, limit=1)

                    # Reset picking state in 2binvoiced only if is currently set to invoiced
                    if picking and picking.invoice_state == 'invoiced':
                        picking.write({'invoice_state': '2binvoiced'})

        return res
