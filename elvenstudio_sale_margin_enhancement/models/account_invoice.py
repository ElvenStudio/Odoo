# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    purchase_price = fields.Float(string='Cost Price', digits=dp.get_precision('Product Price'), readonly=True)

    @api.model
    def create(self, values):

        return super(AccountInvoiceLine, self).create(values)

    # @api.one
    # @api.onchange('price_unit')
    # def price_unit_change(self):
    #     if self.invoice_id.type == 'out_invoice' and \
    #             self.purchase_price > 0 and \
    #             self.price_unit < self.purchase_price:
    #         raise except_orm(_('Price Error!'), _('You can not invoice below the purchase price.'))

    @api.one
    @api.constrains('price_unit', 'purchase_price')
    def _check_seats_limit(self):
        if self.invoice_id.type == 'out_invoice' and \
                not self.env['res.users'].has_group('elvenstudio_sale_margin_enhancement.group_sale_below_purchase_price'):

            date_eval = self.invoice_id.date_invoice or fields.Date.context_today(self)
            if self.invoice_id.currency_id and self.invoice_id.currency_id.id != self.env.user.company_id.currency_id.id:
                from_currency = self.invoice_id.currency_id.with_context(date=date_eval)
                price_unit = from_currency.compute(self.price_unit, self.env.user.company_id.currency_id)
            else:
                price_unit = self.price_unit

            if self.purchase_price > 0 and price_unit < self.purchase_price:
                raise ValidationError(_('You can not sell below the purchase price.'))
