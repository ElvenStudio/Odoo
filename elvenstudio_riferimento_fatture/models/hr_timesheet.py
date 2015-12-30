# -*- encoding: utf-8 -*-

from openerp import models, fields


class HrTimeSheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    rif_da = fields.Integer(string="Riferimento fattura da")
    rif_a = fields.Integer(string="Riferimento fattura a")
