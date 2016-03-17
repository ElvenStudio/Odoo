# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: ElvenStudio
#    Copyright 2015 elvenstudio.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
 'name': 'Tools for connecting odoo to other platforms',
 'license': 'AGPL-3',
 'version': '0.1.0',
 'category': 'Extra Tools',
 'website': 'https://github.com/ElvenStudio/Odoo',
 'summary': "Add a set of tools for export data to other platforms.",
 'description': """
Connect Odoo to other platforms.
===================================================================

Features
-----
* Export any model in csv file
* Send any file in a ftp location
* Query a Url with option parameters
* Send a mail message to a list of user
* Shows the log of the executed actions in Tasks Menu into the ElvenStudio Panel.

Usage
-----
* Go in Configuration -> Technical -> Automation -> Scheduled Action
* Create a new Action, complete the required field and:
    * In the model field, specify elvenstudio.data.connector
    * In the method fields can be used this method:
        * export_to_csv: Export any model in csv file. Params to send are: (filename, model_name, fields,to,export, domain='[optional domain]', log)
        * ftp_send_file: Send any file in a ftp location. Params to send are: (filepath, filename, host, user, pwd, ftp_path, log)
        * open_url: Send any file in a ftp location. Params to send are: (url, params, log)
        * send_msg: send a mail message to a list of users. Params to send are:  (subject, body, list of partner id)
    * all methods except send_msg have the ability to log all the operations (even the completed) setting log=True.
* A new Cron (__Data Connector Log Cleaner__) is available to clean the old entries,  you just need to enable it.

""",
 'author': "ElvenStudio",
 'license': 'AGPL-3',
 'website': 'http://www.elvenstudio.it',

 'images': [
     'images/elvenstudio.png',
 ],

 'depends': [
     'base',
     'elvenstudio_control_panel',
 ],

 'data': [
     'data/data.xml',
     'views/data_connector.xml',
     'security/ir.model.access.csv',
 ],

 'installable': True,
 'application': False,
 }
