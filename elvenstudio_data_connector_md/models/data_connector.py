# -*- coding: utf-8 -*-

from openerp import models, api
import csv
import re
import logging

_logger = logging.getLogger(__name__)


class DataConnector(models.Model):
    _inherit = 'elvenstudio.data.connector'

    @api.model
    def export_to_md(self, filepath, filename, domain, host, user, pwd, ftp_path, url, data_type='listino'):
        status = False
        if data_type == 'listino':
            status = self.export_product_to_md(filepath, filename, domain)
        elif data_type == 'clienti':
            status = self.export_customer_to_md(filepath, filename, domain)

        status = status and \
            self.ftp_send_file(filepath, filename, host, user, pwd, ftp_path) and \
            self.open_url(url, '')

        return status

    @api.model
    def export_customer_to_md(self, filepath, filename, domain):
        status = False
        operation = self.create_operation('export_to_csv')
        operation.execute_operation('res.partner')
        default_domain = [('customer', '=', True)]

        try:
            domain = eval(domain) if domain != '' else []
        except SyntaxError as e:
            operation.error_on_operation(e.message)
        else:
            domain = default_domain + domain
            model = self.env['res.partner']
            customers_to_export = model.search(domain)

            if customers_to_export.ids:
                with open(filepath + '/' + filename, 'w+') as csvFile:
                    writer = csv.writer(csvFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    for customer in customers_to_export:

                        vat = ''
                        if customer.vat:
                            vat_nr = re.findall('\d+', customer.vat)
                            if len(vat_nr) == 1:
                                vat = int(vat_nr[0])

                        payment_term = ''
                        if customer.customer_payment_mode and customer.property_payment_term:
                            payment_term = customer.customer_payment_mode.name + ' ' + \
                                customer.property_payment_term.name

                        extra = 0
                        if customer.property_product_pricelist:
                            extra_nr = re.findall('\-?\d+', customer.property_product_pricelist.name)
                            if len(extra_nr) == 1:
                                extra = -1 * int(extra_nr[0])

                        if vat:
                            row = [
                                customer.id,
                                customer.name.encode('utf-8'),
                                vat,
                                customer.street.encode('utf-8'),
                                customer.city.encode('utf-8'),
                                customer.email.encode('utf-8'),
                                3,  # Il numero di listino gommisti su GCP!, senza questo i clienti non vedono le gomme!
                                extra,  # L'extra!
                                '',  # Tempi di consegna, inutile
                                payment_term.encode('utf-8'),  # Tempi e metodi di consegna
                                max(customer.credit_limit - customer, 0),  # credito restante
                            ]
                            writer.writerow(row)

                    csvFile.close()
                    status = True
                    operation.complete_operation()
            else:
                operation.cancel_operation('No customer selected to export')

        return status

    @api.model
    def export_product_to_md(self, filepath, filename, domain):
        status = False
        operation = self.create_operation('export_to_csv')
        operation.execute_operation('product.product')

        try:
            domain = eval(domain) if domain != '' else []
        except SyntaxError as e:
            operation.error_on_operation(e.message)
        else:
            m = self.env['product.product']
            products_to_export = m.search(domain)
            if products_to_export.ids:
                with open(filepath + '/' + filename, 'w+') as csvFile:
                    writer = csv.writer(csvFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    for product in products_to_export:
                        if product.attribute_set_id:
                            pfu = 0.0
                            ic = ''
                            cv = ''
                            aderenza = ''
                            resistenza = ''
                            rumore = ''
                            battistrada = ''
                            if product.magento_attribute_ids:
                                for attribute in product.magento_attribute_ids:
                                    if 'pfu' == attribute.code:
                                        pfu = attribute.value.split(' - ')[1]
                                    elif 'ic_cv_singola' == attribute.code:
                                        ic = attribute.value[:-1]
                                        cv = attribute.value[-1:]
                                    elif 'aderenza' == attribute.code:
                                        aderenza = attribute.value
                                    elif 'resistenza' == attribute.code:
                                        resistenza = attribute.value
                                    elif 'rumorosita' in attribute.code:
                                        rumore = str(attribute.value) + 'dB'
                                    elif 'battistrada' == attribute.code:
                                        battistrada = attribute.value
                            '''
                            price = 0.0
                            for pricelist in product.pricelist_ids:
                                if "Listino Gommisti (Standard)" == pricelist.name:
                                    price = pricelist.price
                            '''

                            # Fix a crudo per i pfu 2016
                            if '2.15' in str(pfu):
                                pfu = '2.30'
                            elif '0.35' in str(pfu):
                                pfu = '0.38'
                            elif '1.05' in str(pfu):
                                pfu = '1.10'
                            elif '41.6' in str(pfu):
                                pfu = '43.00'
                            elif '113' in str(pfu):
                                pfu = '116.70'
                            elif '16.9' in str(pfu):
                                pfu = '17.60'
                            elif '51.6' in str(pfu):
                                pfu = '53.40'
                            elif '182' in str(pfu):
                                pfu = '188.70'
                            elif '14.15' in str(pfu):
                                pfu = '14.70'
                            elif '34.8' in str(pfu):
                                pfu = '36.00'
                            elif '7.3' in str(pfu):
                                pfu = '7.60'
                            elif '7.8' in str(pfu):
                                pfu = '8.10'
                            elif '68' in str(pfu):
                                pfu = '70.30'
                            elif '21.9' in str(pfu):
                                pfu = '22.80'
                            elif '3.3' in str(pfu):
                                pfu = '3.40'

                            price = product.with_context(pricelist=3).price
                            ip_code = product.default_code
                            if product.ip_code:
                                ip_code = product.ip_code
                            else:
                                default_code = product.default_code.split('-') if product.default_code else []
                                ip_code = default_code[1] if len(default_code) >= 2 else ''

                            imponibile = (price + float(pfu))
                            prezzo_ivato = imponibile + imponibile * 0.22

                            row = [
                                3,
                                ip_code.encode('utf-8'),
                                product.compact_measure.replace('/', '').encode('utf-8') if product.compact_measure else '',
                                product.measure.encode('utf-8'),
                                ic.encode('utf-8'),  # IC
                                cv.encode('utf-8'),  # CV
                                'XL' if product.reinforced else '',
                                'RFT' if product.runflat else '',
                                product.magento_manufacturer.encode('utf-8'),
                                battistrada.encode('utf-8'),
                                'SUMMER' if product.season == 'Estiva' else (
                                    'WINTER' if product.season == 'Invernale' else (
                                        'ALL SEASON' if product.season == 'Quattrostagioni' else '')),
                                'CAR' if product.attribute_set_id.name == 'Pneumatico Auto' else (
                                    'MOTO' if product.attribute_set_id.name == 'Pneumatico Moto' else (
                                        'AUTOCARRO' if product.attribute_set_id.name == 'Pneumatico Autocaro' else '')),
                                price if price else '0.0',
                                pfu.encode('utf-8'),
                                prezzo_ivato.encode('utf-8'),  # vendita + pfu + iva
                                product.qty_available,
                                product.qty_available,
                                '',  # TODO Data prox arrivo
                                product.ean13.encode('utf-8') if product.ean13 else '',
                                '',  # TODO DOT NON USATO
                                aderenza.encode('utf-8'),
                                resistenza.encode('utf-8'),
                                rumore.encode('utf-8'),
                                ''  # TODO NETTO NON USATO
                            ]
                            writer.writerow(row)

                    csvFile.close()
                    status = True
                    operation.complete_operation()
            else:
                operation.cancel_operation('No product selected to export')

        return status
