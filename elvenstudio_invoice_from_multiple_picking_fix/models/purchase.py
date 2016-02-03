# -*- coding: utf-8 -*-

from openerp.osv import  osv


class account_invoice(osv.Model):
    """ Override account_invoice to add Chatter messages on the related purchase
        orders, logging the invoice receipt or payment. """
    _inherit = 'account.invoice'

    # Fix #8654 --- [FIX] purchase, stock_account: invoice_state in stock.move
    def get_invoiced_moves_from_invoices(self, cr, uid, ids, context=None):
        # Inspired from def _get_invoice_line_vals in stock.move
        # To get the move ids  that must be written in state = 'invoiced'
        po_line_obj = self.pool.get('purchase.order.line')
        invoices = self.browse(cr, uid, ids)
        po_line_ids = po_line_obj.search(cr, uid, [('invoice_lines', 'in', invoices.invoice_line.ids)], context=context)
        po_lines = po_line_obj.browse(cr, uid, po_line_ids, context=context)
        res = []
        for line in invoices.invoice_line:
            for po_line in po_lines:
                for move in po_line.move_ids:
                    if move.product_id.id == line.product_id.id and move.invoice_state != 'invoiced' and not(move.id in res):
                        if move.product_uos and line.uos_id.id == move.product_uos.id and line.quantity == move.product_uos_qty:
                            res.append(move.id)
                            break
                        elif line.uos_id.id == move.product_uom.id and line.quantity == move.product_uom_qty:
                            res.append(move.id)
                            break
        return res
