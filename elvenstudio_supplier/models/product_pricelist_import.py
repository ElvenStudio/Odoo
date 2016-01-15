# -*- encoding: utf-8 -*-

from openerp import models, fields, exceptions, api, _
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class ProductPricelistImport(models.Model):
    _name = 'product.pricelist.import'
    _description = 'Product Price List Import'

    name = fields.Char('Load')
    date = fields.Datetime('Date:', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    fails = fields.Integer('Fail Lines:', readonly=True)
    process = fields.Integer('Lines to Process:', readonly=True)
    supplier = fields.Many2one('res.partner', required=True)

    file_lines = fields.One2many(
        comodel_name='product.pricelist.import.line',
        inverse_name='file_import',
        string='Product Price List Lines')

    @api.multi
    def process_lines(self):

        for file_load in self:

            if not file_load.supplier:
                raise exceptions.Warning(_("You must select a Supplier"))

            if not file_load.file_lines:
                raise exceptions.Warning(_("There must be one line at least to process"))

            product_obj = self.env['product.product']
            product_supplier_info_obj = self.env['product.supplierinfo']
            price_list_partner_info_obj = self.env['pricelist.partnerinfo']

            for line in file_load.file_lines:
                # process fail lines
                if line.fail:

                    # search product code
                    if line.code:
                        product_list = product_obj.search([('default_code', '=', line.code)])

                        if len(product_list) == 1:

                            product_tmpl = product_list[0].product_tmpl_id

                            # Cerco il vecchio riferimento al fornitore
                            supplier = product_supplier_info_obj.search([('product_tmpl_id', '=', product_tmpl.id),
                                                                         ('name', '=', file_load.supplier.id)])
                            # Se esiste lo aggiorno
                            if len(supplier) == 1:
                                # TODO trasferire i dati in una model di storicizzazione?
                                supplier.write({
                                    'name': file_load.supplier.id,
                                    'product_tmpl_id': product_tmpl.id,
                                    'product_name': line.supplier_name,
                                    'product_code': line.supplier_code,
                                    'available_qty': line.available_qty,
                                    'delay': line.delay,
                                    'last_modified_date': fields.Datetime.now(),
                                    'supplier_pricelist_import_id': file_load.id
                                })

                                if supplier.pricelist_ids.ids:
                                    # TODO gestire le fasce
                                    supplier.pricelist_ids[0].write({
                                        'min_quantity': product_supplier_info_obj.min_qty,
                                        'price': line.price,
                                        'discount': line.discount,
                                    })

                                else:
                                    # TODO gestire le fasce
                                    price_list_partner_info_obj.create({
                                        'suppinfo_id': supplier.id,
                                        'min_quantity': product_supplier_info_obj.min_qty,
                                        'price': line.price,
                                        'discount': line.discount,
                                    })

                                file_load.fails -= 1
                                line.write({
                                    'product_id': product_tmpl.id,
                                    'fail': False,
                                    'fail_reason': _('Correctly Updated')
                                })

                            # Non esiste e lo creo
                            elif len(supplier) == 0:

                                product_supplier_info_obj = product_supplier_info_obj.create({
                                    'name': file_load.supplier.id,
                                    'product_tmpl_id': product_tmpl.id,
                                    'product_name': line.supplier_name,
                                    'product_code': line.supplier_code,
                                    'available_qty': line.available_qty,
                                    'delay': line.delay,
                                    # 'last_modified_date': fields.Datetime.now(),
                                    'supplier_pricelist_import_id': file_load.id
                                })

                                # TODO gestire le fasce
                                price_list_partner_info_obj.create({
                                    'suppinfo_id': product_supplier_info_obj.id,
                                    'min_quantity': product_supplier_info_obj.min_qty,
                                    'price': line.price,
                                    'discount': line.discount,
                                })

                                file_load.fails -= 1
                                line.write({
                                    'product_id': product_tmpl.id,
                                    'fail': False,
                                    'fail_reason': _('Correctly Added')
                                })

                            # Ci sono almeno due righe con lo stesso fornitore,
                            # è un errore da mostrare
                            else:
                                line.fail_reason = _('Multiple Supplier Line found')

                        elif len(product_list) > 1:
                            line.fail_reason = _('Multiple Products found')

                        else:
                            line.fail_reason = _('Product not found')
                    else:
                        line.fail_reason = _('No Product Code')

                # Cerco i prodotti che hanno un riferimento a questo fornitore
                # e che non sono stati aggiornati dal file perchè devo rimuoverli
                supplier_to_remove = product_supplier_info_obj.search(
                    [
                        ('name', '=', file_load.supplier.id),
                        ('supplier_pricelist_import_id', '!=', file_load.id)
                    ]
                )

                # _logger.warning("da rimuovere " + str(supplier_to_remove))

                # TODO rimuovere MTS + MTO se il prodotto non ha altri fornitori

                # Rimuovo i supplier vecchi
                # Ovvero quelli importati con un listino diverso da quello attuale
                supplier_to_remove.unlink()

        return True


class ProductPricelistImportLine(models.Model):
    _name = 'product.pricelist.import.line'
    _description = 'Product Price List Import Line'

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
