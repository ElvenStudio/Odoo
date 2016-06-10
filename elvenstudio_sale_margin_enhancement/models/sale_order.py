# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import except_orm, ValidationError
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Rewrite margin field for odoo 8 compatibility
    margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)

    product_type = fields.Selection(related='product_id.type', store=True)

    @api.multi
    @api.onchange('product_id', 'product_uom_qty', 'order_id.currency_id')
    def product_id_change_margin(self):
        for line in self:
            # If the line has a product, check if we need to change the purchase_price
            if line.product_id and (line.product_id.cost_price or line.product_id.standard_price):
                purchase_price = line.product_id.cost_price or line.product_id.standard_price

                # If the UOM is different, then we need to recompute the price
                if line.product_uom != line.product_id.uom_id:
                    purchase_price = self.env['product.uom']._compute_price(
                        line.product_id.uom_id.id,
                        purchase_price,
                        to_uom_id=line.product_uom.id
                    )

                # If the company currency is different to the order currency, then we need to convert the price
                frm_cur = self.env.user.company_id.currency_id
                to_cur = line.order_id.currency_id
                if frm_cur != to_cur:
                    ctx = self.env.context.copy()
                    ctx['date'] = line.order_id.date_order
                    purchase_price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)

                # If the new purchase_price is different from the stored,
                #  then we need to save the new one (write only if the price is changed)
                if purchase_price != line.purchase_price:
                    line.purchase_price = purchase_price

    @api.multi
    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            currency = line.order_id.currency_id
            line.margin = currency.round(
                line.price_subtotal - ((line.purchase_price or 0.0) * line.product_uom_qty)
            )

    @api.one
    @api.constrains('price_unit', 'purchase_price')
    def _check_seats_limit(self):
        if not self.env['res.users'].has_group('elvenstudio_sale_margin_enhancement.group_sale_below_purchase_price'):
            if self.price_unit < self.purchase_price:
                raise ValidationError(_('You can not sell below the purchase price.'))

    # @api.one
    # @api.onchange('price_unit')
    # def price_unit_change(self):
    #     if self.purchase_price > 0 and self.price_unit < self.purchase_price:
    #         raise except_orm(_('Price Error!'), _('You can not sell below the purchase price.'))

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=account_id, context=context)
        res['purchase_price'] = line.product_id.cost_price or line.product_id.standard_price or 0.0
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Rewrite margin field for odoo 8 compatibility
    margin = fields.Float(
        compute='_product_margin',
        currency_field='currency_id',
        digits=dp.get_precision('Product Price'),
        store=True,
        help=_("It gives profitability by calculating the difference between the Unit Price and the cost.")
    )

    @api.multi
    @api.depends('order_line.margin')
    def _product_margin(self):
        for order in self:
            order.margin = sum(order.order_line.filtered(lambda r: r.state != 'cancel').mapped('margin'))

    @api.multi
    def recompute_order_margin(self):
        for order in self:
            order.order_line.product_id_change_margin()

    @api.model
    def batch_recompute_margin(self, domain):
        try:
            domain = eval(domain) if domain != '' else []
        except SyntaxError as e:
            raise SyntaxError("Domain Exception: " + str(e.message))
        else:
            order_line_search_domain = [('purchase_price', '=', 0), ('state', 'not in', ['draft', 'cancel'])]

            # Get all lines with the default search domain and the custom search domain
            order_lines = self.env['sale.order.line'].search(order_line_search_domain + domain)

            # Get all orders from lines and recompute margins
            order_lines.mapped('order_id').recompute_order_margin()

            return True
