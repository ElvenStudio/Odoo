# -*- coding: utf-8 -*-

from openerp import models, api
import csv
import re
import logging

_logger = logging.getLogger(__name__)


class DataConnector(models.Model):
    _inherit = 'elvenstudio.data.connector'

    @api.model
    def export_to_md(self, filepath, filename, domain,
                     host, user, pwd, ftp_path, url, data_type='listino', params={}, log=False):
        status = False
        if data_type == 'listino':
            status = self.export_product_to_md(filepath, filename, domain, params, log)
        elif data_type == 'clienti':
            status = self.export_customer_to_md(filepath, filename, domain, params, log)
        elif data_type == 'tyre24':
            status = self.export_product_to_tyre24(filepath, filename, domain, params, log)
        elif data_type == 'easytyre':
            status = self.export_product_to_easytyre(filepath, filename, domain, params, log)

        if host:
            status = status and self.ftp_send_file(filepath, filename, host, user, pwd, ftp_path, log)

        if url:
            status = status and self.open_url(url, '', log)

        return status

    @api.model
    def export_customer_to_md(self, filepath, filename, domain, params=None, log=False):
        if not params:
            params = {}
        status = False
        operation = self.create_operation('export_to_csv')
        operation.execute_operation('res.partner')
        default_domain = [('customer', '=', True)]

        if 'pricelist_ids' not in params or not isinstance(params['pricelist_ids'], dict):
            operation.error_on_operation("Wrong pricelist! Usage: params={pricelisti_ids={id1:discount1,id2:discount2}}")
        else:
            pricelist_ids = params['pricelist_ids']
            try:
                domain = eval(domain) if domain != '' else []
            except SyntaxError as e:
                operation.error_on_operation("Domain Exception: " + str(e.message))
            else:
                domain = default_domain + domain
                model = self.env['res.partner']
                customers_to_export = model.search(domain)

                if customers_to_export.ids:
                    try:
                        with open(filepath + '/' + filename, 'w+') as csvFile:
                            writer = csv.writer(csvFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                            for customer in customers_to_export:

                                if customer.vat and \
                                    customer.property_product_pricelist and \
                                        customer.property_product_pricelist.id in pricelist_ids:

                                    extra = pricelist_ids[customer.property_product_pricelist.id]

                                    vat_nr = re.findall('\d+', customer.vat)
                                    if len(vat_nr) == 1:
                                        # vat = int(vat_nr[0])
                                        vat = vat_nr[0]

                                        payment_term = ''
                                        if customer.customer_payment_mode and customer.property_payment_term:
                                            payment_term = customer.customer_payment_mode.name + ' ' + \
                                                customer.property_payment_term.name
                                            payment_term.replace(';', '')

                                        name = customer.name.encode('utf-8').replace(';', '') if customer.name else ''
                                        street = customer.street.encode('utf-8').replace(';', '') if customer.street else ''
                                        city = customer.city.encode('utf-8').replace(';', '') if customer.city else ''
                                        email = customer.email.encode('utf-8').replace(';', '') if customer.email else ''

                                        row = [
                                            customer.id,
                                            name,
                                            vat,
                                            street,
                                            city,
                                            email,
                                            3,  # Il numero di listino gommisti su GCP!, senza questo i clienti non vedono le gomme!
                                            extra,  # L'extra!
                                            '',  # Tempi di consegna, inutile
                                            payment_term,  # Tempi e metodi di consegna
                                            max(customer.credit_limit - customer.credit, 0),  # credito restante
                                        ]
                                        writer.writerow(row)

                            csvFile.close()
                            status = True
                            if log:
                                operation.complete_operation()
                            else:
                                operation.unlink()
                                operation = False

                    except Exception as e:
                            operation.error_on_operation("Error during data export" +
                                                         (" - " + e.message if e.message else ''))
                else:
                    operation.cancel_operation('No customer selected to export')

        if operation and operation.state == 'error' and 'mail' in params:
            operation.send_log_mail(
                params['mail']['mail_server'],
                params['mail']['login'],
                params['mail']['password'],
                params['mail']['from_address'],
                params['mail']['to_address'],
                'Error during export_customer_to_md execution',
                str(operation.start_date) + ": " + operation.message
            )

        return status

    @api.model
    def export_product_to_md(self, filepath, filename, domain, params={}, log=False):
        status = False
        operation = self.create_operation('export_to_csv')
        operation.execute_operation('product.product')

        if 'pricelist_id' not in params:
            operation.error_on_operation("Wrong pricelist! Usage: params={pricelist_id:id1}")
        else:
            pricelist_id = params['pricelist_id']
            try:
                domain = eval(domain) if domain != '' else []
            except SyntaxError as e:
                operation.error_on_operation("Domain Exception: " + str(e.message))
            else:
                m = self.env['product.product']
                try:
                    products_to_export = m.search(domain)
                except Exception as e:
                    operation.error_on_operation("Domain Exception: " + str(e.message))
                else:
                    if products_to_export.ids:
                        try:
                            with open(filepath + '/' + filename, 'w+') as csvFile:
                                writer = csv.writer(csvFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                for product in products_to_export:
                                    if product.attribute_set_id and product.immediately_usable_qty > 0:
                                        pfu = 0.0
                                        ic = ''
                                        cv = ''
                                        aderenza = ''
                                        resistenza = ''
                                        rumore = ''
                                        battistrada = ''

                                        magento_attribute = product.product_tmpl_id._get_all_magento_attributes()
                                        if 'pfu' in magento_attribute:
                                            pfu = magento_attribute['pfu'].split(' - ')[1]

                                        if 'ic_cv_singola' in magento_attribute:
                                            ic = magento_attribute['ic_cv_singola'][:-1]
                                            cv = magento_attribute['ic_cv_singola'][-1:]

                                        if 'aderenza' in magento_attribute:
                                            aderenza = magento_attribute['aderenza']

                                        if 'resistenza' in magento_attribute:
                                            resistenza = magento_attribute['resistenza']

                                        if 'rumorosita' in magento_attribute:
                                            rumore = str(magento_attribute['rumorosita']) + 'dB'

                                        if 'battistrada' in magento_attribute:
                                            battistrada = magento_attribute['battistrada']


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

                                        stagione = ''
                                        if product.season == 'Invernale':
                                            stagione = 'WINTER'
                                        elif product.season == 'Estiva':
                                            stagione = 'SUMMER'
                                        elif product.season == 'Quattrostagioni':
                                            stagione = 'ALL SEASON'

                                        tipo_auto = ''
                                        if product.attribute_set_id.name == 'Pneumatico Auto':
                                            tipo_auto = 'CAR'
                                        elif product.attribute_set_id.name == 'Pneumatico Moto':
                                            tipo_auto = 'MOTO'
                                        elif product.attribute_set_id.name == 'Pneumatico Autocaro':
                                            tipo_auto = 'AUTOCARRO'

                                        price = product.with_context(pricelist=pricelist_id).price
                                        if product.ip_code:
                                            ip_code = product.ip_code
                                        else:
                                            default_code = product.default_code.split('-') if product.default_code else []
                                            ip_code = default_code[1] if len(default_code) >= 2 else ''

                                        measure = product.compact_measure if product.compact_measure else ''

                                        imponibile = (price + float(pfu))
                                        prezzo_ivato = imponibile + imponibile * 0.22

                                        row = [
                                            3,
                                            ip_code,
                                            measure,
                                            product.measure if product.measure else '',
                                            ic,  # IC
                                            cv,  # CV
                                            'XL' if product.reinforced else '',
                                            'RFT' if product.runflat else '',
                                            product.magento_manufacturer if product.magento_manufacturer else '',
                                            battistrada if battistrada else '',
                                            stagione,
                                            tipo_auto,
                                            price if price else '0.0',
                                            pfu,
                                            prezzo_ivato,  # vendita + pfu + iva
                                            product.immediately_usable_qty,
                                            product.immediately_usable_qty,
                                            '',  # TODO Data prox arrivo
                                            product.ean13 if product.ean13 else '',
                                            '',  # TODO DOT NON USATO
                                            aderenza if aderenza else '',
                                            resistenza if resistenza else '',
                                            rumore if rumore else '',
                                            ''  # TODO NETTO NON USATO
                                        ]
                                        writer.writerow(row)

                                csvFile.close()
                                status = True
                                if log:
                                    operation.complete_operation()
                                else:
                                    operation.unlink()
                                    operation = False

                        except Exception as e:
                            operation.error_on_operation("Error during data export" + (" - " + str(e.message) if e.message else ''))
                    else:
                        operation.cancel_operation('No product selected to export')

        if operation and operation.state == 'error' and 'mail' in params:
            operation.send_log_mail(
                params['mail']['mail_server'],
                params['mail']['login'],
                params['mail']['password'],
                params['mail']['from_address'],
                params['mail']['to_address'],
                'Error during export_product_to_md execution',
                str(operation.start_date) + ": " + str(operation.message)
            )

        return status

    @api.model
    def export_product_to_tyre24(self, filepath, filename, domain, params={}, log=False):
        status = False
        operation = self.create_operation('export_to_csv')
        operation.execute_operation('product.product')

        if 'pricelist_id' not in params:
            operation.error_on_operation("Wrong pricelist! Usage: params={pricelist_id:id1}")
        else:
            pricelist_id = params['pricelist_id']
            try:
                domain = eval(domain) if domain != '' else []
            except SyntaxError as e:
                operation.error_on_operation("Domain Exception " + str(e.message))
            else:
                m = self.env['product.product']
                try:
                    products_to_export = m.search(domain)
                except Exception as e:
                    operation.error_on_operation("Domain Exception " + str(e.message))
                else:
                    if products_to_export.ids:
                        try:
                            with open(filepath + '/' + filename, 'w+') as csvFile:
                                writer = csv.writer(csvFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                for product in products_to_export:
                                    if product.attribute_set_id and product.immediately_usable_qty > 0:
                                        ipcode = self._get_ipcode_from_default_code(product)
                                        if ipcode or product.ean13:
                                            price = product.with_context(pricelist=pricelist_id).price

                                            row = [
                                                ipcode,
                                                ipcode,
                                                product.name,
                                                product.name,
                                                '',
                                                product.magento_manufacturer,
                                                price,
                                                '',
                                                '',
                                                '',
                                                '',
                                                '',
                                                '',
                                                product.immediately_usable_qty,
                                                product.ean13,
                                                ''
                                            ]
                                            writer.writerow(row)

                                csvFile.close()
                                status = True
                                if log:
                                    operation.complete_operation()
                                else:
                                    operation.unlink()
                                    operation = False

                        except Exception as e:
                            operation.error_on_operation("Error during data export" + (" - " + str(e.message) if e.message else ''))
                    else:
                        operation.cancel_operation('No product selected to export')

        if operation and operation.state == 'error' and 'mail' in params:
            operation.send_log_mail(
                params['mail']['mail_server'],
                params['mail']['login'],
                params['mail']['password'],
                params['mail']['from_address'],
                params['mail']['to_address'],
                'Error during export_product_to_tyre24 execution',
                str(operation.start_date) + ": " + str(operation.message)
            )

        return status

    @api.model
    def export_product_to_easytyre(self, filepath, filename, domain, params={}, log=False):
        status = False
        operation = self.create_operation('export_to_csv')
        operation.execute_operation('product.product')

        if 'pricelist_id' not in params:
            operation.error_on_operation("Wrong pricelist! Usage: params={pricelist_id:id1}")
        else:
            pricelist_id = params['pricelist_id']
            try:
                domain = eval(domain) if domain != '' else []
            except SyntaxError as e:
                operation.error_on_operation("Domain Exception " + str(e.message))
            else:
                m = self.env['product.product']
                try:
                    products_to_export = m.search(domain)
                except Exception as e:
                    operation.error_on_operation("Domain Exception " + str(e.message))
                else:
                    if products_to_export.ids:
                        try:
                            with open(filepath + '/' + filename, 'w+') as csvFile:
                                writer = csv.writer(csvFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                for product in products_to_export:
                                    if product.attribute_set_id and product.immediately_usable_qty > 0:
                                        ipcode = self._get_ipcode_from_default_code(product)
                                        if ipcode or product.ean13:
                                            price = product.with_context(pricelist=pricelist_id).price

                                            larghezza = ''
                                            sezione = ''
                                            cerchio = ''
                                            if product.compact_measure:
                                                measure = product.compact_measure.split('/')
                                                if len(measure) == 3:
                                                    larghezza = measure[0]
                                                    sezione = measure[1]
                                                    cerchio = measure[2]

                                            pfu = 0.0
                                            ic = ''
                                            cv = ''
                                            battistrada = ''

                                            magento_attribute = product.product_tmpl_id._get_all_magento_attributes()
                                            if 'pfu' in magento_attribute:
                                                pfu = magento_attribute['pfu'].split(' - ')[1]

                                            if 'ic_cv_singola' in magento_attribute:
                                                ic = magento_attribute['ic_cv_singola'][:-1]
                                                cv = magento_attribute['ic_cv_singola'][-1:]

                                            if 'battistrada' in magento_attribute:
                                                battistrada = magento_attribute['battistrada']

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

                                            row = [
                                                product.ean13,
                                                '',  # non si sa, chiedere a easytyre
                                                ipcode,
                                                product.immediately_usable_qty,
                                                price,
                                                product.magento_manufacturer,
                                                product.name,
                                                larghezza,
                                                sezione,
                                                cerchio,
                                                ic,
                                                cv,
                                                'XL' if product.reinforced else '',
                                                'SUMMER' if product.season == 'Estiva' else (
                                                    'WINTER' if product.season == 'Invernale' else (
                                                        'ALL SEASON' if product.season == 'Quattrostagioni' else '')),
                                                'RFT' if product.runflat else '',
                                                '',  # settore
                                                battistrada,
                                                pfu
                                            ]
                                            writer.writerow(row)

                                csvFile.close()
                                status = True

                                if log:
                                    operation.complete_operation()
                                else:
                                    operation.unlink()
                                    operation = False

                        except Exception as e:
                            operation.error_on_operation("Error during data export" + (" - " + str(e.message) if e.message else ''))
                    else:
                        operation.cancel_operation('No product selected to export')

        if operation and operation.state == 'error' and 'mail' in params:
            operation.send_log_mail(
                params['mail']['mail_server'],
                params['mail']['login'],
                params['mail']['password'],
                params['mail']['from_address'],
                params['mail']['to_address'],
                'Error during export_product_to_easytyre execution',
                str(operation.start_date) + ": " + str(operation.message)
            )

        return status

    @staticmethod
    def _get_ipcode_from_default_code(product):
        if product.ip_code:
            ip_code = product.ip_code
        else:
            default_code = product.default_code.split('-') if product.default_code else []
            ip_code = default_code[1] if len(default_code) >= 2 else ''

        return ip_code
