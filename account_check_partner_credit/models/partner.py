# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class Partner(osv.osv):
    _inherit = 'res.partner'

    def _credit_search(self, cr, uid, obj, name, args, context=None):
        return super(Partner, self)._credit_search(cr, uid, obj, name, args, context=context)

    def _debit_search(self, cr, uid, obj, name, args, context=None):
        return super(Partner, self)._debit_search(cr, uid, obj, name, args, context=context)

    def _credit_debit_get(self, cr, uid, ids, field_names, arg, context=None):
        res = super(Partner, self)._credit_debit_get(cr, uid, ids, field_names, arg, context=context)

        for partner_id in res:
            checks_on_hold_id = self.pool.get('account.check').search(
                cr, uid,
                [
                    ('source_partner_id', '=', partner_id), ('type', '=', 'third_check'), ('state', '=', 'holding')
                ],
                context=context
            )

            # Access to record with SUPERUSER ID to avoid restriction rules
            checks_on_hold = self.pool.get('account.check').browse(cr, 1, checks_on_hold_id, context=context)

            checks_credit = sum(check.amount for check in checks_on_hold)

            res[partner_id]['credit'] += checks_credit

        return res

    _columns = {
        'credit': fields.function(
            _credit_debit_get,
            fnct_search=_credit_search,
            string='Total Receivable',
            multi='dc',
            help="Total amount this customer owes you."),
        'debit': fields.function(
            _credit_debit_get,
            fnct_search=_debit_search,
            string='Total Payable',
            multi='dc',
            help="Total amount you have to pay to this supplier."),
    }
