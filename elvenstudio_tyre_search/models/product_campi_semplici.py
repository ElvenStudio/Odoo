# -*- coding: utf-8 -*-

from openerp import models, fields, api
import ast

import logging

_logger = logging.getLogger(__name__)

'''
    TODO Mancano alcuni attributi, forse non utili alla ricerca
        - PFU
        - NHS
        - Self Seal
        - Snow Flake
        - Bordo Cerchio
        - Off Road
'''


class AttributeCode(object):
    Pneumatico = 'Pneumatico'
    Larghezza = 'larghezza'
    Sezione = 'sezione'
    Cerchio = 'cerchio'
    Struttura = 'struttura'
    IpCode = 'codice_produttore'
    Marca = 'manufacturer'
    Stagione = 'stagione'
    Tube = 'tube'
    Asse = 'posizione'
    Resistenza = 'resistenza'
    Aderenza = 'aderenza'
    Rumore = 'rumorosita'
    MudSnow = 'm_s'
    Runflat = 'runflat'
    Reinforced = 'rinforzato'
    IC_CV_singola = 'ic_cv_singola'
    IC_CV_gemellata = 'ic_cv_gemellata'
    Asse_Sterzante = 'sterzante'
    Asse_Trattivo = 'trattivo'
    Asse_Rimorchio = 'rimorchio'


class MagentoProductAttributes(models.Model):
    """
    Estendo product.attributes per aggiungere l'etichetta e la chiave di un attributo magento,
    in quanto il modulo di base le ha referenziate in una model più interna.
    """
    _inherit = "product.attributes"

    label = fields.Char(related='attribute_id.label', readonly=True, copy=False)
    code = fields.Char(related='attribute_id.name', readonly=True, copy=False)


class Product(models.Model):
    _inherit = "product.template"

    magento_attribute_ids = fields.One2many(
        comodel_name='product.attributes',
        inverse_name='fkey_product',
        string='Attributi Magento')

    tipo_pneumatico = fields.Char(string='Tipo Pneumatico', compute='_get_tipo_pneumatico', store=True, index=True)

    compact_measure = fields.Char(
        string='Misura compatta',
        help='Misura compatta per la ricerca veloce. Esempio: 195/55/15.',
        index=True
    )

    ip_code = fields.Char(string='Ip Code', index=True)
    magento_manufacturer = fields.Char(string='Marca', index=True)
    etichetta_europea = fields.Char(string='Etichetta Europea', index=True)

    # TODO Modificare la ricerca per permettere ricerche del tipo: IC > valore e CV > Valore
    ic_cv = fields.Char(string='ICCV', index=True)

    measure = fields.Char(string='Misura')
    season = fields.Char(string='Stagione', index=True)
    tube = fields.Char(string='Camera', index=True)
    asse = fields.Char(string='Asse', index=True)
    mud_snow = fields.Boolean(string='M+S', index=True)
    runflat = fields.Boolean(string='RFT', index=True)
    reinforced = fields.Boolean(string='XL', index=True)
    asse_sterzante = fields.Boolean(string='Sterzante', index=True)
    asse_trattivo = fields.Boolean(string='Trattivo', index=True)
    asse_rimorchio = fields.Boolean(string='Rimorchio', index=True)

    @api.one
    @api.depends('attribute_set_id')
    def _get_tipo_pneumatico(self):
        self.tipo_pneumatico = 'none'
        if self.attribute_set_id:
            attribute_set_name = self.attribute_set_id.name

            if 'Autocarro' in attribute_set_name:
                self.tipo_pneumatico = 'autocarro'
            elif 'Auto' in attribute_set_name:
                self.tipo_pneumatico = 'auto'
            elif 'Moto' in attribute_set_name:
                self.tipo_pneumatico = 'moto'

        # Se viene aggiornato l'attribute set, forzo l'aggiornamento dei dati del pneumatico
        #self.env['product.template'].browse([self.id]).write({'update_tyre_attribute': True})

    @api.model
    def create(self, values):
        product = super(Product, self).create(values)
        self.env['product.template'].browse([self.id]).write({'update_tyre_attribute': True})

        return product

    @api.multi
    def write(self, values):
        if 'update_tyre_attribute' in values and self.magento_attribute_ids:
            attributes = self._get_dict_from_magento_attribute(self.magento_attribute_ids)

            attributes_to_write = {}

            # Attributi per la Misura
            larghezza = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Larghezza))
            sezione = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Sezione))
            cerchio = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Cerchio))
            struttura = self._get_dict_value(attributes, AttributeCode.Struttura)

            # MISURA COMPATTA
            attributes_to_write['compact_measure'] = larghezza + \
                (self._get_separator(sezione) if larghezza != '' else '') + sezione + \
                self._get_separator(larghezza + sezione) + cerchio

            # MISURA
            attributes_to_write['measure'] = larghezza + \
                (self._get_separator(sezione) if larghezza != '' else '') + sezione + \
                self._get_separator(larghezza + sezione, separator=' ') + struttura + cerchio

            # IP CODE
            attributes_to_write['ip_code'] = self._get_dict_value(attributes, AttributeCode.IpCode)

            # MARCA
            attributes_to_write['magento_manufacturer'] = self._get_dict_value(attributes, AttributeCode.Marca)

            # STAGIONE
            attributes_to_write['season'] = self._get_dict_value(attributes, AttributeCode.Stagione)

            # TT/TL
            tube = self._get_dict_value(attributes, AttributeCode.Tube)
            attributes_to_write['tube'] = 'Tube Type' if tube == 'TT' else 'Tube Less' if tube == 'TL' else ''

            # ASSE
            attributes_to_write['asse'] = self._get_dict_value(attributes, AttributeCode.Asse)

            # ETICHETTA EUROPEA
            resistenza = self._get_dict_value(attributes, AttributeCode.Resistenza)
            aderenza = self._get_dict_value(attributes, AttributeCode.Aderenza)
            rumore = self._get_dict_value(attributes, AttributeCode.Rumore)

            try:
                rumore += 'dB' if isinstance(int(rumore), int) else ''
            except ValueError:
                pass

            attributes_to_write['etichetta_europea'] = resistenza + \
                ((' ' + aderenza) if aderenza != '' else '') + \
                ((' ' + rumore) if aderenza + rumore != '' else '')

            # M+S
            attributes_to_write['mud_snow'] = self._get_dict_value(attributes, AttributeCode.MudSnow) == 'SI'

            # RFT
            attributes_to_write['runflat'] = self._get_dict_value(attributes, AttributeCode.Runflat) == 'SI'

            # XL
            attributes_to_write['reinforced'] = self._get_dict_value(attributes, AttributeCode.Reinforced) == 'SI'

            # IC CV
            iccv_singola = self._get_dict_value(attributes, AttributeCode.IC_CV_singola)
            iccv_gemellata = self._get_dict_value(attributes, AttributeCode.IC_CV_gemellata)

            try:
                iccv_singola = ast.literal_eval(iccv_singola)
            except SyntaxError:
                pass

            try:
                iccv_gemellata = ast.literal_eval(iccv_gemellata)
            except SyntaxError:
                pass

            # _logger.warning("IC CV Singola " + str(iccv_singola))
            # _logger.warning("IC CV Gemellata " + str(iccv_gemellata))

            ic_cv = ''

            # Verifico che non ci sia una situazione del tipo, perchè errata:
            #  - IC CV Singola      -> 98V
            #  - IC CV Gemellata    -> [94V,97R]
            if not isinstance(iccv_singola, list) and isinstance(iccv_gemellata, list):
                pass

            elif isinstance(iccv_singola, list) and isinstance(iccv_gemellata, list):
                ic_cv = self._eval_ic_cv(iccv_singola[0], iccv_gemellata[0]) + \
                    "(" + self._eval_ic_cv(iccv_singola[1], iccv_gemellata[1]) + ")"

            elif isinstance(iccv_singola, list) and iccv_gemellata != '':
                ic_cv = self._eval_ic_cv(iccv_singola[0], iccv_gemellata) + "(" + iccv_singola[1] + ")"

            elif isinstance(iccv_singola, list) and (iccv_gemellata == '' or iccv_gemellata is None):
                ic_cv = iccv_singola[0] + "(" + iccv_singola[1] + ")"

            elif iccv_singola != '' and iccv_gemellata != '':
                ic_cv = self._eval_ic_cv(iccv_singola, iccv_gemellata)

            elif iccv_singola != '':
                ic_cv = iccv_singola

            attributes_to_write['ic_cv'] = ic_cv

            # ASSE STERZANTE
            attributes_to_write['asse_sterzante'] = self._get_dict_value(attributes, AttributeCode.Asse_Sterzante) == 'SI'

            # ASSE TRATTIVO
            attributes_to_write['asse_trattivo'] = self._get_dict_value(attributes, AttributeCode.Asse_Trattivo) == 'SI'

            # ASSE RIMORCHIO
            attributes_to_write['asse_rimorchio'] = self._get_dict_value(attributes, AttributeCode.Asse_Rimorchio) == 'SI'

            result = self.write(attributes_to_write)

        else:
            result = super(Product, self).write(values)

        return result

    @staticmethod
    def _get_dict_from_magento_attribute(attributes):
        results = dict()

        if attributes:
            for attribute in attributes:
                key = attribute.code

                if AttributeCode.Larghezza in attribute.code:
                    key = AttributeCode.Larghezza

                if AttributeCode.Sezione in attribute.code:
                    key = AttributeCode.Sezione

                if AttributeCode.Cerchio in attribute.code:
                    key = AttributeCode.Cerchio

                if AttributeCode.Asse in attribute.code:
                    key = AttributeCode.Asse

                results[key] = attribute.value

        return results

    @staticmethod
    def _get_measure_value(value, default=''):
        try:
            result = value if isinstance(float(value), float) else default
        except ValueError:
            result = value if '/' in value else default

        return result

    @staticmethod
    def _get_separator(value, separator='/', empty_separator=''):
        return separator if value != '' else empty_separator

    @staticmethod
    def _get_dict_value(dictionary, key, default=''):
        return dictionary[key] if key in dictionary else default

    @staticmethod
    def _eval_ic_cv(iccv_singola, iccv_gemellata):
        return iccv_gemellata[:-1] + "/" + iccv_singola
