# -*- coding: utf-8 -*-

import openerp
from openerp import netsvc, SUPERUSER_ID, _
from openerp.osv import fields, osv

import logging
import time

_logger = logging.getLogger(__name__)


def str2tuple(s):
    return eval('tuple(%s)' % (s or ''))


class IrCron(osv.osv):
    _inherit = 'ir.cron'

    _columns = {
        'cron_log_ids': fields.one2many('ir.cron.log', 'cron_id', string=_('Cron Logs')),
        'log_days_to_keep': fields.integer(string=_('Remove logs after x days'))
    }

    _defaults = {
        'log_days_to_keep': 1
    }

    def _callback(self, cr, uid, model_name, method_name, args, job_id):
        """ Run the method associated to a given job

        It takes care of logging and exception handling.

        :param model_name: model name on which the job method is located.
        :param method_name: name of the method to call when this job is processed.
        :param args: arguments of the method (without the usual self, cr, uid).
        :param job_id: job id.
        """

        cron_log_obj = self.pool.get('ir.cron.log')

        cron_log_id = cron_log_obj.create(cr, SUPERUSER_ID, {'cron_id': job_id}, context=None)
        date_start = None
        try:
            args = str2tuple(args)
            openerp.modules.registry.RegistryManager.check_registry_signaling(cr.dbname)
            registry = openerp.registry(cr.dbname)
            if model_name in registry:
                model = registry[model_name]
                if hasattr(model, method_name):
                    log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
                    netsvc.log(_logger, logging.DEBUG, 'cron.object.execute',
                               (cr.dbname, uid, '*', model_name, method_name) + tuple(args), depth=log_depth)

                    # Set the cron status as in-progress
                    cron_log_obj.write(cr, SUPERUSER_ID, [cron_log_id], {'status': 'in-progress'}, context=None)

                    # Executes the method and tracks the elapsed time
                    start_time = time.time()
                    date_start = openerp.fields.Datetime.now()
                    getattr(model, method_name)(cr, uid, *args)
                    date_end = openerp.fields.Datetime.now()
                    end_time = time.time()

                    # Cron executed succesfully, store the result
                    cron_log_obj.write(cr, SUPERUSER_ID, [cron_log_id],
                                       {'status': 'done', 'date_start': date_start, 'date_end': date_end}, context=None)

                    if _logger.isEnabledFor(logging.DEBUG):
                        _logger.debug('%.3fs (%s, %s)' % (end_time - start_time, model_name, method_name))

                    openerp.modules.registry.RegistryManager.signal_caches_change(cr.dbname)
                else:
                    msg = "Method `%s.%s` does not exist." % (model_name, method_name)
                    _logger.warning(msg)

                    # No method found, save the unused call
                    cron_log_obj.write(cr, SUPERUSER_ID, [cron_log_id],
                                       {'status': 'error', 'error_message': msg}, context=None)

            else:
                msg = "Model `%s` does not exist." % model_name
                _logger.warning(msg)

                # No model found, save the unused call
                cron_log_obj.write(cr, SUPERUSER_ID, [cron_log_id],
                                   {'status': 'error', 'error_message': msg}, context=None)

        except Exception, e:
            # An exception is raised during execution, save the result
            date_end = openerp.fields.Datetime.now()
            cron_log_obj.write(
                cr, SUPERUSER_ID, [cron_log_id],
                {
                    'status': 'error',
                    'date_start': date_start,
                    'date_end': date_end,
                    'error_message': e.message
                }, context=None)

            self._handle_callback_exception(cr, uid, model_name, method_name, args, job_id, e)

IrCron()
