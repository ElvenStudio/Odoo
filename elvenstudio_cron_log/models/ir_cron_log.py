# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta


class IrCronLog(models.Model):
    _name = 'ir.cron.log'

    cron_id = fields.Many2one('ir.cron', _("Cron"), required=True)
    state = fields.Selection(
        [
            ('draft', _('Draft')),
            ('in-progress', _('In Progress')),
            ('done', _('Done')),
            ('error', _('Error')),
        ],
        string=_('Status'),
        index=True,
        readonly=True,
        default='draft')

    date_start = fields.Datetime(readonly=True)
    date_end = fields.Datetime(readonly=True)
    message = fields.Char(readonly=True)
    duration = fields.Char(compute='_get_duration', readonly=True)
    error_message = fields.Char(readonly=True)

    @api.one
    @api.depends('date_start', 'date_end')
    def _get_duration(self):
        if self.date_end and self.date_start:
            d_frm_obj = datetime.strptime(self.date_start, DEFAULT_SERVER_DATETIME_FORMAT)
            d_to_obj = datetime.strptime(self.date_end, DEFAULT_SERVER_DATETIME_FORMAT)
            self.duration = str(d_to_obj - d_frm_obj)
        else:
            self.duration = ''

    @api.model
    def clean_logs(self):
        crons = self.env['ir.cron'].search([])
        today = date.today()
        for cron in crons:
            date_before = today - timedelta(days=cron.log_days_to_keep)
            self.env['ir.cron.log'].search(
                [
                    ('cron_id', '=', cron.id),
                    ('create_date', '<', fields.Date.to_string(date_before))
                ]
            ).unlink()
        return True
