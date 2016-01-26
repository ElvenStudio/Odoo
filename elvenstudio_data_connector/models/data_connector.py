# -*- coding: utf-8 -*-

from openerp import models, fields, api
import csv
import ftplib
import urllib
import urllib2
import logging

_logger = logging.getLogger(__name__)


class DataConnector(models.BaseModel):
    _name = 'elvenstudio.data.connector'

    impacted_model = fields.Many2one('ir.model', 'model')
    command = fields.Char(size=100, index=True, required=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in-progress', 'In Progress'),
            ('done', 'Done'),
            ('error', 'Error'),
            ('cancel', 'Cancel')
        ],
        string='Status',
        index=True,
        readonly=True,
        default='draft')
    start_date = fields.Datetime(readonly=True)
    end_date = fields.Datetime(readonly=True)
    message = fields.Char(size=255, readonly=True)

    @api.one
    def exist_model(self, model_name):
        return model_name in self.env.registry

    @api.model
    def create_operation(self, command_name=''):
        return self.create({'command': command_name})

    @api.one
    def cancel_operation(self, message=''):
        self.write({'state': 'cancel', 'message': message})

    @api.one
    def execute_operation(self, model=''):
        self.write({
            'impacted_model': self.env['ir.model'].search([('model', '=', model)]).id,
            'start_date': fields.Datetime.now(),
            'state': 'in-progress'
        })

    @api.one
    def complete_operation(self):
        self.write({'end_date': fields.Datetime.now(), 'state': 'done'})

    @api.one
    def error_on_operation(self, message=''):
        self.write({
            'state': 'error',
            'end_date': fields.Datetime.now(),
            'message': message
        })

    @api.model
    def export_to_csv(self, filename, model_name, *fields_to_export, **kwargs):
        status = False
        operation = self.create_operation('export_to_csv')
        if not fields_to_export:
            operation.cancel_operation('No fields defined')
        else:
            domain = []
            if 'domain' in kwargs:
                domain = kwargs['domain']
            if operation.exist_model(model_name):
                operation.execute_operation(model_name)
                model = self.env[model_name]
                objs_to_export = model.search(domain)
                if objs_to_export.ids:
                    with open(filename, 'w+') as csvFile:
                        writer = csv.DictWriter(csvFile, fields_to_export)
                        writer.writeheader()

                        for obj in objs_to_export:
                            row = {k: (str(obj[k]).encode('utf-8') if k in obj else '') for k in fields_to_export}
                            writer.writerow(row)

                        csvFile.close()
                        status = True
                        operation.complete_operation()
                else:
                    operation.error_on_operation('No data to export with this domain: ' + str(domain))
            else:
                operation.error_on_operation('Model ' + str(model_name) + ' not found')

        return status

    @api.model
    def ftp_send_file(self, filepath, filename, host, user, pwd, ftp_path):
        status = False
        operation = self.create_operation('ftp_send_file')
        if filepath and filename and host and user and pwd and ftp_path:
            operation.execute_operation()
            try:
                ftp = ftplib.FTP(host)
                ftp.login(user, pwd)
                ftp.cwd(ftp_path)
                file_to_send = open(filepath + '/' + filename, 'r')
                ftp.storlines('STOR ' + filename, file_to_send)
                ftp.quit()
                file_to_send.close()
                status = True
                operation.complete_operation()
            except Exception as e:
                operation.error_on_operation(e.message)
        else:
            operation.cancel_operation('Missing Params')

        return status

    @api.model
    def open_url(self, url, param):
        status = False
        operation = self.create_operation('open_url')
        if url:
            operation.execute_operation()
            if param:
                data = urllib.urlencode(param)
                url += '?' + data

            try:
                request = urllib2.urlopen(url)
            except urllib2.URLError as e:
                operation.error_on_operation(e.message)
            else:
                if request.msg == 'OK':
                    # TODO Error 500 page?
                    status = True
                    operation.complete_operation()
                else:
                    operation.error_on_operation(request.msg)
        else:
            operation.cancel_operation('Missing Urls')

        return status
