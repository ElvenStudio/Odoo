# -*- coding: utf-8 -*-

from itertools import chain
from openerp import models, fields, api, _, exceptions
import openerp.addons.decimal_precision as dp
import time
import logging

# _log = logging.getLogger(__name__)


class ProductPricelistMargin(models.Model):
    _inherit = 'product.pricelist'

    product_cost = fields.Float(
        compute='_get_product_cost',
        digits=dp.get_precision('Product Price'),
        help=_('Product Cost'))

    net_margin = fields.Float(
        string=_('Margin'),
        compute='_get_net_margin',
        digits=dp.get_precision('Product Price'),
        help=_('Product net margin'))

    margin_percent = fields.Char(string=_('Margin Percentage'), compute='_get_margin_percent')
    markup = fields.Char(compute='_get_markup')

    price_with_taxes = fields.Float(
        compute='_get_product_price_with_taxes',
        digits=dp.get_precision('Product Price'),
        help=_('Product Price With Taxes'))

    @api.one
    def _get_product_price(self):
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)

        if product_id:
            price = self.env['product.product'].browse(product_id).with_context(pricelist=self.id).price
        elif template_id:
            price = self.env['product.template'].browse(template_id).with_context(pricelist=self.id).price
        else:
            price = 0

        return price

    @api.one
    def _get_net_margin(self):
        self.net_margin = self._get_product_price()[0] - self.product_cost

    @api.one
    def _get_margin_percent(self):
        price = self._get_product_price()[0]
        self.margin_percent = str(round((self.net_margin / price if price > 0 else 0.00) * 100, 2)) + '%'

    @api.one
    def _get_markup(self):
        cost = self.product_cost
        self.markup = str(round((self.net_margin / cost if cost > 0 else 0.00) * 100, 2)) + '%'

    @api.one
    def _get_product_cost(self):
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)
        partner_id = self._context.get('partner_id', False)
        quantity = self._context.get('partner_id', 1)

        if partner_id:
            partner_id = self.env['res.partner'].browse(partner_id)

        product = False
        if product_id:
            product = self.env['product.product'].browse(product_id)
        elif template_id:
            product = self.env['product.template'].browse(template_id)

        self.product_cost = self._get_cost(self, [(product, quantity, partner_id)])

    @api.one
    def _get_product_price_with_taxes(self):
        product_id = self._context.get('product_id', False)
        template_id = self._context.get('template_id', False)
        if product_id:
            self.price_with_taxes = self.env['product.product'].browse(product_id).taxes_id.compute_all(
                self.price, 1.0)['total_included']
        elif template_id:
            self.price_with_taxes = self.env['product.template'].browse(template_id).taxes_id.compute_all(
                self.price, 1.0)['total_included']

    @api.multi
    def _get_cost(self, pricelist, products_by_qty_by_partner):
        context = self._context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        date = date[0:10]

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        prices = []

        if not products or not products[0]:
            return {}

        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and \
                    ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise exceptions.except_orm(
                _('Warning!'),
                _("At least one pricelist has no active version !\nPlease create or activate one.")
            )

        categ_ids = {}
        for p in products:
            if p.categ_id:
                categ = p.categ_id
                while categ:
                    categ_ids[categ.id] = True
                    categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
                'AND (product_id IS NULL OR (product_id = any(%s))) '
                'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
                'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(self._cr, self._uid, item_ids, context=context)

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            # rule_id = False
            price = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            # price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        self._cr, self._uid, context['uom'], qty, product.uom_id.id or product.uos_id.id)
                except exceptions.except_orm:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and \
                            (product.product_variant_count > 1 or
                                product.product_variant_ids[0].id != rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._get_cost(rule.base_pricelist_id, [(product, qty, partner)])
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        # price_uom_id = qty_uom_id
                        price = currency_obj.compute(
                            self._cr, self._uid, ptype_src, pricelist.currency_id.id,
                            price_tmp, round=False, context=context
                        )
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        seller = product.seller_ids[0]
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(
                                self._cr, self._uid, qty_uom_id, qty, to_uom_id=seller_uom)

                        # price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(self._cr, self._uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e. qty_uom_id
                    # price_uom_id = qty_uom_id
                    price = currency_obj.compute(
                        self._cr, self._uid, price_type.currency_id.id, pricelist.currency_id.id,
                        product_obj._price_get(
                            self._cr, self._uid, [product], price_type.field, context=context)[product.id],
                        round=False, context=context)

                if price:
                    prices.append(price)

        if prices:
            price = prices[0]
        else:
            price = 0.0

        return price
