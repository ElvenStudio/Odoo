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

    compact_measure = fields.Char(
        string='Misura compatta',
        help='Misura compatta per la ricerca veloce. Esempio: 195/55/15.',
        compute='_get_compact_measure',
        store=True,
        index=True,
        search='_search_compact_measure',
        inverse='_write_compact_measure'
    )

    ip_code = fields.Char(
        string='Ip Code',
        compute='_get_ip_code',
        store=True,
        index=True,
        search='_search_ip_code'
    )

    magento_manufacturer = fields.Char(
        string='Marca',
        compute='_get_magento_manufacturer',
        store=True,
        index=True,
        search='_search_magento_manufacturer'
    )

    etichetta_europea = fields.Char(
        string='Etichetta Europea',
        compute='_get_etichetta_europea',
        store=True,
        index=True,
        search='_search_etichetta_europea'
    )

    # TODO Modificare la ricerca per permettere ricerche del tipo: IC > valore e CV > Valore
    ic_cv = fields.Char(
        string='ICCV',
        compute='_get_ic_cv',
        store=True,
        index=True,
        search='_search_ic_cv'
    )

    measure = fields.Char(string='Misura', compute='_get_measure', store=True, inverse='_write_measure')
    season = fields.Char(string='Stagione', compute='_get_season', store=True, index=True)
    tube = fields.Char(string='Camera', compute='_get_tube', store=True, index=True)
    asse = fields.Char(string='Asse', compute='_get_asse', store=True, index=True)
    mud_snow = fields.Boolean(string='M+S', compute='_get_mud_snow', store=True, index=True)
    runflat = fields.Boolean(string='RFT', compute='_get_runflat', store=True, index=True)
    reinforced = fields.Boolean(string='XL', compute='_get_reinforced', store=True, index=True)
    asse_sterzante = fields.Boolean(string='Sterzante', compute='_get_asse_sterzante', store=True, index=True)
    asse_trattivo = fields.Boolean(string='Trattivo', compute='_get_asse_trattivo', store=True, index=True)
    asse_rimorchio = fields.Boolean(string='Rimorchio', compute='_get_asse_rimorchio', store=True, index=True)
    tipo_pneumatico = fields.Char(string='Tipo di Pneumatico', compute='_get_tipo_pneumatico', store=True, index=True)

    @api.one
    @api.depends('attribute_set_id')
    def _get_tipo_pneumatico(self):
        self.tipo_pneumatico = 'none'
        if self.attribute_set_id:
            self.tipo_pneumatico = self.attribute_set_id.name

        # _logger.warning("Agg. prod. " + str(self.id))

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

        self._magento_attributes = str(attributes).replace('"', "\"")

    @api.one
    @api.depends('_magento_attributes')
    def _get_compact_measure(self):
        attributes = ast.literal_eval(self._magento_attributes)

        larghezza = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Larghezza))
        sezione = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Sezione))
        cerchio = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Cerchio))

        self.compact_measure = larghezza + \
            (self._get_separator(sezione) if larghezza != '' else '') + sezione + \
            self._get_separator(larghezza + sezione) + cerchio

    @api.one
    def _write_compact_measure(self):

        if self.compact_measure:
            measure_values = self.compact_measure.split("/")
            size_measure_values = len(measure_values)

            to_save = True

            if size_measure_values == 3:
                larghezza = measure_values[0]
                sezione = measure_values[1]
                cerchio = measure_values[2]

            elif size_measure_values == 2:
                larghezza = measure_values[0]
                sezione = ''
                cerchio = measure_values[1]

            else:
                _logger.error("Wrong measure written!")
                to_save = False

            if to_save:
                attributes = dict()

                # Recupero la struttura se presente
                if self._magento_attributes:
                    attributes = ast.literal_eval(self._magento_attributes)

                struttura = self._get_dict_value(attributes, AttributeCode.Struttura, 'R')

                self.measure = larghezza + \
                    (self._get_separator(sezione) if larghezza != '' else '') + sezione + \
                    self._get_separator(larghezza + sezione, separator=' ') + struttura + cerchio

    @api.one
    @api.depends('_magento_attributes')
    def _get_measure(self):
        attributes = ast.literal_eval(self._magento_attributes)

        larghezza = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Larghezza))
        sezione = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Sezione))
        cerchio = self._get_measure_value(self._get_dict_value(attributes, AttributeCode.Cerchio))
        struttura = self._get_dict_value(attributes, AttributeCode.Struttura)

        self.measure = larghezza + \
            (self._get_separator(sezione) if larghezza != '' else '') + sezione + \
            self._get_separator(larghezza + sezione, separator=' ') + struttura + cerchio

    @api.one
    def _write_measure(self):
        # Dummy Write
        # Enable save on computed stored field
        # Depends on _write_compact_measure
        return True

    @api.one
    @api.depends('_magento_attributes')
    def _get_ip_code(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.ip_code = self._get_dict_value(attributes, AttributeCode.IpCode)

    @api.one
    @api.depends('_magento_attributes')
    def _get_magento_manufacturer(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.magento_manufacturer = self._get_dict_value(attributes, AttributeCode.Marca)

    @api.one
    @api.depends('_magento_attributes')
    def _get_season(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.season = self._get_dict_value(attributes, AttributeCode.Stagione)

    @api.one
    @api.depends('_magento_attributes')
    def _get_tube(self):
        attributes = ast.literal_eval(self._magento_attributes)
        tube = self._get_dict_value(attributes, AttributeCode.Tube)
        self.tube = ('Tube Type' if tube == 'TT' else ('Tube Less' if tube == 'TL' else ''))

    @api.one
    @api.depends('_magento_attributes')
    def _get_asse(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.asse = self._get_dict_value(attributes, AttributeCode.Asse)

    @api.one
    @api.depends('_magento_attributes')
    def _get_etichetta_europea(self):
        attributes = ast.literal_eval(self._magento_attributes)
        resistenza = self._get_dict_value(attributes, AttributeCode.Resistenza)
        aderenza = self._get_dict_value(attributes, AttributeCode.Aderenza)
        rumore = self._get_dict_value(attributes, AttributeCode.Rumore)

        try:
            rumore += 'dB' if isinstance(int(rumore), float) else ''
        except ValueError:
            pass

        self.etichetta_europea = resistenza + \
            ((' ' + aderenza) if aderenza != '' else '') + \
            ((' ' + rumore) if aderenza + rumore != '' else '')

    @api.one
    @api.depends('_magento_attributes')
    def _get_mud_snow(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.mud_snow = self._get_dict_value(attributes, AttributeCode.MudSnow) == 'SI'

    @api.one
    @api.depends('_magento_attributes')
    def _get_runflat(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.runflat = self._get_dict_value(attributes, AttributeCode.Runflat) == 'SI'

    @api.one
    @api.depends('_magento_attributes')
    def _get_reinforced(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.reinforced = self._get_dict_value(attributes, AttributeCode.Reinforced) == 'SI'

    @api.one
    @api.depends('_magento_attributes')
    def _get_ic_cv(self):
        self.ic_cv = ''
        attributes = ast.literal_eval(self._magento_attributes)

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

        # Verifico che non ci sia una situazione del tipo, perchè errata:
        #  - IC CV Singola      -> 98V
        #  - IC CV Gemellata    -> [94V,97R]
        if not isinstance(iccv_singola, list) and isinstance(iccv_gemellata, list):
            pass

        elif isinstance(iccv_singola, list) and isinstance(iccv_gemellata, list):
            self.ic_cv = self._eval_ic_cv(iccv_singola[0], iccv_gemellata[0]) + \
                "(" + self._eval_ic_cv(iccv_singola[1], iccv_gemellata[1]) + ")"

        elif isinstance(iccv_singola, list) and iccv_gemellata != '':
            self.ic_cv = self._eval_ic_cv(iccv_singola[0], iccv_gemellata) + "(" + iccv_singola[1] + ")"

        elif isinstance(iccv_singola, list) and (iccv_gemellata == '' or iccv_gemellata is None):
            self.ic_cv = iccv_singola[0] + "(" + iccv_singola[1] + ")"

        elif iccv_singola != '' and iccv_gemellata != '':
            self.ic_cv = self._eval_ic_cv(iccv_singola, iccv_gemellata)

        elif iccv_singola != '':
            self.ic_cv = iccv_singola

    @api.one
    @api.depends('_magento_attributes')
    def _get_asse_sterzante(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.asse_sterzante = self._get_dict_value(attributes, AttributeCode.Asse_Sterzante) == 'SI'

    @api.one
    @api.depends('_magento_attributes')
    def _get_asse_trattivo(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.asse_trattivo = self._get_dict_value(attributes, AttributeCode.Asse_Trattivo) == 'SI'

    @api.one
    @api.depends('_magento_attributes')
    def _get_asse_rimorchio(self):
        attributes = ast.literal_eval(self._magento_attributes)
        self.asse_rimorchio = self._get_dict_value(attributes, AttributeCode.Asse_Rimorchio) == 'SI'

    @staticmethod
    def _search_compact_measure(operator, value):
        return [('measure', operator, value)]

    @staticmethod
    def _search_ip_code(operator, value):
        return [('ip_code', operator, value)]

    @staticmethod
    def _search_magento_manufacturer(operator, value):
        return [('magento_manufacturer', operator, value)]

    @staticmethod
    def _search_etichetta_europea(operator, value):
        return [('etichetta_europea', operator, value)]

    @staticmethod
    def _search_ic_cv(operator, value):
        return [('ic_cv', operator, value)]

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