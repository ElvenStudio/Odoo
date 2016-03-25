# -*- coding: utf-8 -*-

import logging
import ast

from openerp import models, fields, api
from openerp.addons.elvenstudio_tyre.models.attribute_code import AttributeCode as AttrCode

_log = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.template"

    # Campi base della misura
    larghezza = fields.Char(string='Larghezza', size=10)
    sezione = fields.Char(string='Sezione', size=10)
    struttura = fields.Char(string='Struttura', size=5)
    cerchio = fields.Char(string='Cerchio', size=10)
    iccv_singola = fields.Char(string='ICCV Singola', size=50)
    iccv_gemellata = fields.Char(string='ICCV Gemellata', size=50)

    # Campi calcolati
    measure = fields.Char(string='Misura', index=True, size=50)
    compact_measure = fields.Char(string='Misura compatta', index=True, size=50)
    slashed_measure = fields.Char(string='Misura', index=True, size=50)
    iccv = fields.Char(string='ICCV', index=True, size=50)

    def _init_measure(self, cr, uid, context=None):
        _log.warning("Data Initialization")
        i = 0
        prod_obj = self.pool.get('product.template')
        products = prod_obj.search(cr, uid, [])
        for p in products:
            p = prod_obj.browse(cr, uid, p)
            data_to_save = p._get_measure_to_save_from_magento()
            if data_to_save:
                p.write(data_to_save)

            i += 1
            if i % 100 == 0:
                _log.warning(str(i) + " product updated")

        return True

    @api.model
    def get_attribute_to_save_from_magento(self):
        attributes = super(Product, self).get_attribute_to_save_from_magento()
        attributes.update(self._get_measure_to_save_from_magento())
        return attributes

    @api.model
    def _get_measure_to_save_from_magento(self):
        attributes = dict()
        magento_attrib = self._get_magento_attributes(self._get_measure_attribute_codes())

        if magento_attrib:
            larghezza = self._get_measure_value(self._get_dict_value(magento_attrib, AttrCode.Larghezza))
            sezione = self._get_measure_value(self._get_dict_value(magento_attrib, AttrCode.Sezione))
            cerchio = self._get_measure_value(self._get_dict_value(magento_attrib, AttrCode.Cerchio))
            struttura = self._get_dict_value(magento_attrib, AttrCode.Struttura)

            iccv_singola = self._get_dict_value(magento_attrib, AttrCode.IC_CV_singola)
            iccv_gemellata = self._get_dict_value(magento_attrib, AttrCode.IC_CV_gemellata)

            # Verifico che le iccv non siano delle liste memorizzate come stringhe
            # In tal caso le devo convertire con ast
            try:
                iccv_singola_converted = ast.literal_eval(iccv_singola)
            except SyntaxError:
                iccv_singola_converted = iccv_singola

            try:
                iccv_gemellata_converted = ast.literal_eval(iccv_gemellata)
            except SyntaxError:
                iccv_gemellata_converted = iccv_gemellata

            measure = self.get_measure(larghezza, sezione, struttura, cerchio)
            compact_measure = self.get_compact_measure(larghezza, sezione, cerchio)
            slashed_measure = self.get_slashed_measure(larghezza, sezione, cerchio)

            iccv = self.get_iccv(iccv_singola_converted, iccv_gemellata_converted)

            # Memorizzo i dati base del prodotto
            attributes['larghezza'] = larghezza
            attributes['sezione'] = sezione
            attributes['cerchio'] = cerchio
            attributes['struttura'] = struttura
            attributes['iccv'] = iccv

            # Mantengo le versioni "stringhizzate" per le successive conversioni
            attributes['iccv_singola'] = iccv_singola
            attributes['iccv_gemellata'] = iccv_gemellata

            # memorizzo i campi calcolati della misura
            attributes['measure'] = measure
            attributes['compact_measure'] = compact_measure
            attributes['slashed_measure'] = slashed_measure

            # Evito il controllo durante la scrittura in quanto già effettuato
            attributes['tyre_update'] = True

        return attributes

    @api.model
    def get_measure(self, larghezza, sezione, struttura, cerchio, separator="/"):
        return str(larghezza) + str(separator) + str(sezione) + " " + str(struttura) + str(cerchio)

    @api.model
    def get_compact_measure(self, larghezza, sezione, cerchio):
        return str(larghezza).replace(".", "").replace(",", "") + \
            str(sezione).replace(".", "").replace(",", "") + \
            str(cerchio).replace(".", "").replace(",", "")

    @api.model
    def get_slashed_measure(self, larghezza, sezione, cerchio):
        return str(larghezza).replace(".", "").replace(",", "") + \
            (self._get_separator(sezione) if larghezza != '' else '') + \
            str(sezione).replace(".", "").replace(",", "") + \
            self._get_separator(str(larghezza) + str(sezione)) + \
            str(cerchio).replace(".", "").replace(",", "")

    @api.model
    def get_iccv(self, iccv_singola, iccv_gemellata):
        iccv = ''
        # Verifico che non ci sia una situazione del tipo, perchè errata:
        #  - IC CV Singola      -> 98V
        #  - IC CV Gemellata    -> [94V,97R]
        if not isinstance(iccv_singola, list) and isinstance(iccv_gemellata, list):
            pass

        elif isinstance(iccv_singola, list) and isinstance(iccv_gemellata, list):
            iccv = self._eval_ic_cv(iccv_singola[0], iccv_gemellata[0]) + \
                "(" + self._eval_ic_cv(iccv_singola[1], iccv_gemellata[1]) + ")"

        elif isinstance(iccv_singola, list) and iccv_gemellata != '':
            iccv = self._eval_ic_cv(iccv_singola[0], iccv_gemellata) + "(" + iccv_singola[1] + ")"

        elif isinstance(iccv_singola, list) and (iccv_gemellata == '' or iccv_gemellata is None):
            iccv = iccv_singola[0] + "(" + iccv_singola[1] + ")"

        elif iccv_singola != '' and iccv_gemellata != '':
            iccv = self._eval_ic_cv(iccv_singola, iccv_gemellata)

        elif iccv_singola != '':
            iccv = iccv_singola

        return iccv

    @api.multi
    def write(self, values):
        result = False
        if 'tyre_update' not in values and \
                ('larghezza' in values or 'sezione' in values or 'struttura' in values or 'cerchio' in values):

            values_to_write = {i: j for i, j in values.items()
                               if i != 'larghezza' and i != 'sezione' and i != 'struttura' and i != 'cerchio'}

            for product in self:
                larghezza = values['larghezza'] if 'larghezza' in values else product.larghezza
                sezione = values['sezione'] if 'sezione' in values else product.sezione
                struttura = values['struttura'] if 'struttura' in values else product.struttura
                cerchio = values['cerchio'] if 'cerchio' in values else product.cerchio

                measure = product.get_measure(larghezza, sezione, struttura, cerchio)
                compact_measure = product.get_compact_measure(larghezza, sezione, cerchio)
                slashed_measure = product.get_slashed_measure(larghezza, sezione, cerchio)

                values_to_write['larghezza'] = larghezza
                values_to_write['sezione'] = sezione
                values_to_write['struttura'] = struttura
                values_to_write['cerchio'] = cerchio
                values_to_write['measure'] = measure
                values_to_write['compact_measure'] = compact_measure
                values_to_write['slashed_measure'] = slashed_measure

                # Evito il controllo durante la scrittura in quanto già effettuato
                values_to_write['tyre_update'] = True

                result &= product.write(values_to_write)
        else:
            if 'tyre_update' in values:
                values.pop('tyre_update')
            result = super(Product, self).write(values)

        return result

    @staticmethod
    def _get_measure_attribute_codes():
        return {
            # larghezza
            AttrCode.Larghezza_Auto: AttrCode.Larghezza,
            AttrCode.Larghezza_Moto: AttrCode.Larghezza,
            AttrCode.Larghezza_Autocarro: AttrCode.Larghezza,

            # sezione
            AttrCode.Sezione_Auto: AttrCode.Sezione,
            AttrCode.Sezione_Moto: AttrCode.Sezione,
            AttrCode.Sezione_Autocarro: AttrCode.Sezione,

            # cerchio
            AttrCode.Cerchio_Auto: AttrCode.Cerchio,
            AttrCode.Cerchio_Moto: AttrCode.Cerchio,
            AttrCode.Cerchio_Autocarro: AttrCode.Cerchio,

            AttrCode.Struttura: AttrCode.Struttura,

            AttrCode.IC_CV_singola: AttrCode.IC_CV_singola,
            AttrCode.IC_CV_gemellata: AttrCode.IC_CV_gemellata,
        }

    @staticmethod
    def _get_measure_value(value, default=''):
        try:
            result = value if isinstance(float(value), float) else default
        except ValueError:
            result = value if '/' in value or "," in value else default

        return result

    @staticmethod
    def _eval_ic_cv(iccv_singola, iccv_gemellata):
        return iccv_gemellata[:-1] + "/" + iccv_singola

    @staticmethod
    def _get_separator(value, separator='/', empty_separator=''):
        return separator if value != '' else empty_separator
