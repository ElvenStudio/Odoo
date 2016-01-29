# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class AccountVoucherLine(osv.osv):
    _inherit = 'account.voucher.line'

    _columns = {
        'move_name': fields.related(
            'move_line_id',
            'name',
            relation='account.move.line',
            type='char',
            string='Name',
            readonly=1
        ),
    }


class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        result = super(AccountVoucher, self).recompute_voucher_lines(
            cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context)

        move_line_obj = self.pool['account.move.line']

        if 'value' in result:
            if 'line_cr_ids' in result['value'] and result['value']['line_cr_ids']:
                for move in result['value']['line_cr_ids']:
                    if isinstance(move, dict) and move['move_line_id']:
                        move['move_name'] = move_line_obj.browse(
                            cr, uid, move['move_line_id'], context).name

            if 'line_dr_ids' in result['value'] and result['value']['line_dr_ids']:
                for move in result['value']['line_cr_ids']:
                    if isinstance(move, dict) and move['move_line_id']:
                        move['move_name'] = move_line_obj.browse(
                            cr, uid, move['move_line_id'], context).name

        return result
