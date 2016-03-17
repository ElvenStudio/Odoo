# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class ProductPricelistImport(models.Model):
    _name = 'product.pricelist.import'
    _description = 'Product Price List Import'

    name = fields.Char('Pricelist')
    date = fields.Datetime('Date:', readonly=True)
    process_start_date = fields.Datetime('Process Start Date', readonly=True)
    process_end_date = fields.Datetime('Process End Date', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    fails = fields.Integer('Fail Lines', readonly=True)
    process = fields.Integer('Lines to Process', readonly=True)

    supplier = fields.Many2one('res.partner', required=True)
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')

    file_lines = fields.One2many(
        comodel_name='product.pricelist.import.line',
        inverse_name='file_import',
        string='Product Price List Lines')

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('overdue', 'Overdue'),
            ('ended', 'Ended'),
            ('cancel', 'Cancel')
        ],
        string='Status',
        index=True,
        readonly=True,
        default='draft')

    @api.multi
    def process_pricelist(self):

        for pricelist in self:

            if pricelist.start_date and pricelist.start_date > fields.Datetime.now():
                raise Warning("The pricelist is not activable yet.")

            start_date = fields.Datetime.now()

            if not pricelist.supplier:
                raise Warning(_("You must select a Supplier"))

            if not pricelist.file_lines:
                raise Warning(_("There must be one line at least to process"))

            product_obj = self.env['product.product']
            product_supplier_info_obj = self.env['product.supplierinfo']
            price_list_partner_info_obj = self.env['pricelist.partnerinfo']

            product_to_sort = set()
            product_to_check_mto = set()
            multi_supplier_lines = []
            multi_product_lines = []
            no_product_lines = []
            no_product_code_lines = []

            for line in pricelist.file_lines:
                # process fail lines
                if line.fail:

                    # search product code
                    if line.code:
                        product_list = product_obj.search([('default_code', '=', line.code)])

                        if len(product_list) == 1:

                            product_tmpl = product_list[0].product_tmpl_id

                            # Cerco il vecchio riferimento al fornitore
                            supplier = product_supplier_info_obj.search([('product_tmpl_id', '=', product_tmpl.id),
                                                                         ('name', '=', pricelist.supplier.id)])
                            # Se esiste lo aggiorno
                            if len(supplier) == 1:
                                # TODO trasferire i dati in una model di storicizzazione?
                                supplier.write({
                                    'name': pricelist.supplier.id,
                                    'product_tmpl_id': product_tmpl.id,
                                    'product_name': line.supplier_name,
                                    'product_code': line.supplier_code,
                                    'available_qty': line.available_qty,
                                    'delay': line.delay,
                                    'last_modified_date': fields.Datetime.now(),
                                    'supplier_pricelist_import_id': pricelist.id,
                                    'sort_suppliers': False,
                                })

                                if supplier.pricelist_ids.ids:
                                    # TODO gestire le fasce
                                    supplier.pricelist_ids[0].write({
                                        'min_quantity': product_supplier_info_obj.min_qty,
                                        'price': line.price,
                                        'discount': line.discount,
                                        'sort_suppliers': False,
                                    })

                                else:
                                    # TODO gestire le fasce
                                    price_list_partner_info_obj.create({
                                        'suppinfo_id': supplier.id,
                                        'min_quantity': product_supplier_info_obj.min_qty,
                                        'price': line.price,
                                        'discount': line.discount,
                                        'sort_suppliers': False,
                                    })

                                line.write({
                                    'product_id': product_tmpl.id,
                                    'fail': False,
                                    'fail_reason': _('Correctly Updated')
                                })

                                # Se effettuo una modifica, sul prodotto devo verificare l'ordine dei fornitori
                                # Devo verificare anche che le stock.location.route
                                product_to_sort.add(product_tmpl.id)
                                product_to_check_mto.add(product_tmpl.id)

                            # Non esiste e lo creo
                            elif len(supplier) == 0:

                                product_supplier_info_obj = product_supplier_info_obj.create({
                                    'name': pricelist.supplier.id,
                                    'product_tmpl_id': product_tmpl.id,
                                    'product_name': line.supplier_name,
                                    'product_code': line.supplier_code,
                                    'available_qty': line.available_qty,
                                    'delay': line.delay,
                                    # 'last_modified_date': fields.Datetime.now(),
                                    'supplier_pricelist_import_id': pricelist.id,
                                    'sort_suppliers': False,
                                    'update_mto_route': False,
                                })

                                # TODO gestire le fasce
                                price_list_partner_info_obj.create({
                                    'suppinfo_id': product_supplier_info_obj.id,
                                    'min_quantity': product_supplier_info_obj.min_qty,
                                    'price': line.price,
                                    'discount': line.discount,
                                    'sort_suppliers': False,
                                })

                                line.write({
                                    'product_id': product_tmpl.id,
                                    'fail': False,
                                    'fail_reason': _('Correctly Added')
                                })

                                # Se aggiungo un fornitore, devo sicuramente verificare che le stock.location.route
                                # siano attive o da aggiornare
                                # Ma devo anche aggiornare l'ordine dei fornitori, perchè potrebbero
                                # essercene altri già presenti
                                product_to_check_mto.add(product_tmpl.id)
                                product_to_sort.add(product_tmpl.id)

                            # Ci sono almeno due righe con lo stesso fornitore,
                            # è un errore da mostrare
                            else:
                                # line.fail_reason = _('Multiple Supplier Line found') -- avoid write
                                multi_supplier_lines.append(line.id)

                        elif len(product_list) > 1:
                            # line.fail_reason = _('Multiple Products found') -- avoid write
                            multi_product_lines.append(line.id)

                        else:
                            # line.fail_reason = _('Product not found') -- avoid write
                            no_product_lines.append(line.id)

                    else:
                        # line.fail_reason = _('No Product Code') -- avoid write
                        no_product_code_lines.append(line.id)

            # Aggiorno le righe che hanno lo stesso fornitore più volte
            if multi_supplier_lines:
                pricelist.file_lines.browse(multi_supplier_lines).write({'fail_reason': _('Multiple Supplier Line found')})

            # Aggiorno le righe che hanno più prodotti con lo stesso codice
            if multi_product_lines:
                pricelist.file_lines.browse(multi_product_lines).write({'fail_reason': _('Multiple Products found')})

            # Aggiorno le righe che non hanno prodotti
            if no_product_lines:
                pricelist.file_lines.browse(no_product_lines).write({'fail_reason': _('Product not found')})

            # Aggiorno le righe che non hanno il codice prodotto
            if no_product_code_lines:
                pricelist.file_lines.browse(no_product_lines).write({'fail_reason': _('No Product Code')})

            if product_to_sort:
                self.env['product.template'].browse(list(product_to_sort)).sort_suppliers()

            if product_to_check_mto:
                self.env['product.template'].browse(list(product_to_check_mto)).update_mto_route()

            end_date = fields.Datetime.now()
            pricelist.write({'process_start_date': start_date, 'process_end_date': end_date, 'state': 'active'})

        return True

    @api.multi
    def action_deactivate_pricelist(self):
        product_supplier_info_obj = self.env['product.supplierinfo']
        for pricelist in self:
            if pricelist.state != 'active' and pricelist.state != 'overdue':
                raise Warning('Cannot deactivate a pricelist that is not in active or overdue state.')

            if pricelist.end_date and pricelist.end_date > fields.Datetime.now():
                raise Warning('Cannot deactivate a pricelist with a future deactivation date.')

            product_supplier_info_obj.search([('supplier_pricelist_import_id', '=', pricelist.id)]).unlink()
            pricelist.write({'state': 'ended', 'update_fail_line': False})

    @api.multi
    def action_check_overdue(self):
        self.browse(
            map(
                lambda p: p.id,
                filter(
                    lambda p: p.end_date and p.state == 'active' and p.end_date < fields.Datetime.now(),
                    self
                )
            )
        ).write({'state': 'overdue', 'update_fail_line': False})

    @api.multi
    def action_cancel_pricelist(self):
        for pricelist in self:
            if pricelist.state == 'draft':
                pricelist.write({'state': 'cancel'})
            else:
                raise Warning('Cannot cancel a pricelist that is already in active or overdue state. '
                              'Try deactivating it.')

    @api.multi
    def action_draft_pricelist(self):
        for pricelist in self:
            if pricelist.state == 'cancel':
                pricelist.write({'state': 'draft'})
            else:
                raise Warning('Cannot set to draft a pricelist that is already in active, overdue or ended state.')

    @api.model
    def activate_pricelist(self):
        self.search([
            ('state', '=', 'draft'),
            ('start_date', '!=', False),
            ('start_date', '<', fields.Datetime.now())
        ]).process_pricelist()

    @api.model
    def check_overdue_pricelist(self):
        self.search([
            ('state', '=', 'active'),
            ('end_date', '!=', False),
            ('end_date', '<', fields.Datetime.now())
        ]).write({'state': 'overdue', 'update_fail_line': False})

    @api.model
    def deactivate_pricelist(self):
        self.search([
            ('state', 'in', ['active', 'overdue']),
            ('end_date', '!=', False),
            ('end_date', '<', fields.Datetime.now())
        ]).action_deactivate_pricelist()

    @api.multi
    def write(self, values):
        if 'update_fail_line' not in values or values['update_fail_line']:
            result = super(ProductPricelistImport, self).write(values)

            # Recompute fall line
            for pricelist in self:
                pricelist.write({
                    'process': len(pricelist.file_lines),
                    'fails': pricelist.file_lines.count_fail_lines(),
                    'update_fail_line': False
                })
        else:
            values.pop('update_fail_line')
            result = super(ProductPricelistImport, self).write(values)

        return result


class ProductPricelistImportLine(models.Model):
    _name = 'product.pricelist.import.line'
    _description = 'Product Price List Import Line'
    _order = 'fail desc'

    code = fields.Char('Product Code')
    supplier_code = fields.Char('Supplier Product Code')
    supplier_name = fields.Char('Supplier Product Name')

    price = fields.Float('Product Price', required=True)
    discount = fields.Float('Product Discount')

    available_qty = fields.Float('Available Quantity',
                                 required=True,
                                 help="The available quantity that can be purchased from this supplier, expressed"
                                 " in the supplier Product Unit of Measure if not empty, in the default"
                                 " unit of measure of the product otherwise.",
                                 digits=dp.get_precision('Product Unit of Measure'))

    delay = fields.Integer('Delivery Lead Time',
                           required=True,
                           help="Lead time in days between the confirmation of the purchase order and the receipt "
                                "of the products in your warehouse. Used by the scheduler for automatic computation "
                                "of the purchase order planning.")

    product_id = fields.Many2one('product.template',
                                 string='Product',
                                 required=False,
                                 help='The Product related during the load process')

    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_import = fields.Many2one('product.pricelist.import', 'File Import', required=True)

    @api.multi
    def count_fail_lines(self):
        return sum(map(lambda line: 1 if line.fail else 0, self))
