# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class AccountVoucherLine(osv.osv):
    _inherit = 'account.voucher.line'

    _columns = {
        'move_name': fields.related('move_line_id', 'name',
                                    relation='account.move.line',
                                    type='char',
                                    string='Name',
                                    readonly=1),
    }
