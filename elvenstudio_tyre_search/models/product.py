# -*- coding: utf-8 -*-

from openerp import models, fields, api
import ast
import csv

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
    Sezione_Auto = 'sezione_auto'
    Sezione_Moto = 'sezione_moto'
    Sezione_Autocarro = 'sezione_autocarro'
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

    _magento_attributes = fields.Char(compute="_get_magento_attributes", store=True)

    measure = fields.Char(string='Misura', compute='_get_measure', store=True, index=True)

    compact_measure = fields.Char(
        string='Misura compatta',
        help='Misura, esempio: 1955515.',
        compute='_get_compact_measure',
        store=True,
        index=True
    )

    ip_code = fields.Char(string='Ip Code', store=True, index=True)
    magento_manufacturer = fields.Char(string='Marca', store=True, index=True)

    tipo_pneumatico = fields.Char(string='Tipo di Pneumatico', compute='_get_tipo_pneumatico', store=True, index=True)

    # TODO Modificare la ricerca per permettere ricerche del tipo: IC > valore e CV > Valore
    ic_cv = fields.Char(string='ICCV', store=True, index=True)

    larghezza = fields.Char(store=True, index=True)
    sezione = fields.Char(store=True, index=True)
    cerchio = fields.Char(store=True, index=True)
    struttura = fields.Char(store=True, index=True)

    season = fields.Char(string='Stagione', store=True, index=True)
    tube = fields.Char(string='Camera', store=True, index=True)
    asse = fields.Char(string='Asse', store=True, index=True)
    mud_snow = fields.Boolean(string='M+S', store=True, index=True)
    runflat = fields.Boolean(string='RFT', store=True, index=True)
    reinforced = fields.Boolean(string='XL', store=True, index=True)
    etichetta_europea = fields.Char(string='Etichetta Europea', store=True, index=True)

    asse_sterzante = fields.Boolean(string='Sterzante', store=True, index=True)
    asse_trattivo = fields.Boolean(string='Trattivo', store=True, index=True)
    asse_rimorchio = fields.Boolean(string='Rimorchio', store=True, index=True)

    @api.one
    @api.depends('attribute_set_id')
    def _get_tipo_pneumatico(self):
        self.tipo_pneumatico = 'none'
        if self.attribute_set_id:
            self.tipo_pneumatico = self.attribute_set_id.name

    @api.one
    @api.depends('magento_attribute_ids')
    def _get_magento_attributes(self):
        attributes = dict()

        if self.attribute_set_id:
            if AttributeCode.Pneumatico in self.attribute_set_id.name:
                for attribute in self.magento_attribute_ids:
                    key = attribute.code

                    if AttributeCode.Larghezza in attribute.code:
                        key = AttributeCode.Larghezza

                    if AttributeCode.Sezione_Auto == attribute.code or \
                        AttributeCode.Sezione_Moto == attribute.code or \
                            AttributeCode.Sezione_Autocarro == attribute.code:
                        key = AttributeCode.Sezione

                    if AttributeCode.Cerchio in attribute.code:
                        key = AttributeCode.Cerchio

                    if AttributeCode.Asse in attribute.code:
                        key = AttributeCode.Asse

                    attributes[key] = attribute.value

        ip_code = self._get_dict_value(attributes, AttributeCode.IpCode)
        magento_manufacturer = self._get_dict_value(attributes, AttributeCode.Marca)
        season = self._get_dict_value(attributes, AttributeCode.Stagione)
        asse = self._get_dict_value(attributes, AttributeCode.Asse)
        mud_snow = self._get_dict_value(attributes, AttributeCode.MudSnow) == 'SI'
        runflat = self._get_dict_value(attributes, AttributeCode.Runflat) == 'SI'
        reinforced = self._get_dict_value(attributes, AttributeCode.Reinforced) == 'SI'

        # Assi Autocarro
        asse_sterzante = self._get_dict_value(attributes, AttributeCode.Asse_Sterzante) == 'SI'
        asse_trattivo = self._get_dict_value(attributes, AttributeCode.Asse_Trattivo) == 'SI'
        asse_rimorchio = self._get_dict_value(attributes, AttributeCode.Asse_Rimorchio) == 'SI'

        # Tube
        tube = self._get_dict_value(attributes, AttributeCode.Tube)
        tube = ('Tube Type' if tube == 'TT' else ('Tube Less' if tube == 'TL' else ''))
        ic_cv = self._get_ic_cv(attributes)
        etichetta_europea = self._get_etichetta_europea(attributes)

        # Misura
        larghezza = self._get_dict_value(attribute, AttributeCode.Larghezza)
        sezione = self._get_dict_value(attribute, AttributeCode.Sezione, '-')
        cerchio = self._get_dict_value(attribute, AttributeCode.Cerchio)
        struttura = self._get_dict_value(attribute, AttributeCode.Struttura, '-')

        _magento_attributes = str(attributes).replace('"', "\"")

        # Salvo tutti i campi calcolati nei rispettivi campi della model
        self.write({
            'ip_code': ip_code,
            'magento_manufacturer': magento_manufacturer,
            'season': season,
            'asse': asse,
            'mud_snow': mud_snow,
            'runflat': runflat,
            'reinforced': reinforced,
            'asse_sterzante': asse_sterzante,
            'asse_trattivo': asse_trattivo,
            'asse_rimorchio': asse_rimorchio,
            'tube': tube,
            'ic_cv': ic_cv,
            'etichetta_europea': etichetta_europea,
            'larghezza': larghezza,
            'sezione': sezione,
            'cerchio': cerchio,
            'struttura': struttura,
            '_magento_attributes': _magento_attributes
        })

    @api.one
    @api.depends('_magento_attributes', 'larghezza', 'sezione', 'cerchio')
    def _get_compact_measure(self):
        lar = str(self.larghezza) if self.larghezza else ''
        sez = str(self.sezione) if self.sezione else ''
        cer = str(self.cerchio) if self.cerchio else ''
        self.compact_measure = lar + sez + cer

    @api.one
    @api.depends('_magento_attributes', 'larghezza', 'sezione', 'cerchio')
    def _get_measure(self):
        lar = str(self.larghezza) if self.larghezza else ''
        sez = str(self.sezione) if self.sezione else ''
        cer = str(self.cerchio) if self.cerchio else ''
        strut = str(self.struttura) if self.struttura else ''

        self.measure = lar + (self._get_separator(sez) if lar != '' else '') + sez + \
            self._get_separator(lar + sez, separator=' ') + strut + cer

    @api.one
    def _get_ic_cv(self, attributes):
        ic_cv = ''

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

        return ic_cv

    @api.one
    def _get_etichetta_europea(self, attributes):
        resistenza = self._get_dict_value(attributes, AttributeCode.Resistenza)
        aderenza = self._get_dict_value(attributes, AttributeCode.Aderenza)
        rumore = self._get_dict_value(attributes, AttributeCode.Rumore)

        try:
            rumore += 'dB' if isinstance(int(rumore), float) else ''
        except ValueError:
            pass

        return resistenza + \
            ((' ' + aderenza) if aderenza != '' else '') + \
            ((' ' + rumore) if aderenza + rumore != '' else '')

    @staticmethod
    def _get_dict_value(dictionary, key, default=''):
        return dictionary[key] if key in dictionary else default

    @staticmethod
    def _eval_ic_cv(iccv_singola, iccv_gemellata):
        return iccv_gemellata[:-1] + "/" + iccv_singola

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

