A set of useful set of tool that connect Odoo to other platforms.
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
        * export_to_csv: Export any model in csv file. Params to send are: (filename, model_name, fields,to,export, domain='[optional domain]')
        * ftp_send_file: Send any file in a ftp location. Params to send are: (filepath, filename, host, user, pwd, ftp_path)
        * open_url: Send any file in a ftp location. Params to send are: (url, params)
        * send_msg: send a mail message to a list of users. Params to send are:  (subject, body, list of partner id)