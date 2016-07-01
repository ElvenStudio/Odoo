# -*- coding: utf-8 -*-

import xmlrpclib


class MagentoXmlRpcClient(object):

    XML_RPC_PATH = '/index.php/api/xmlrpc'
    CALL_CHUNK = 50

    def __init__(self, base_url, user, pwd, xml_rcp_path=XML_RPC_PATH):
        self._url = base_url + xml_rcp_path
        self._user = user
        self._pwd = pwd
        self._server = None
        self._session = None

    def connect(self):
        if not self._server and not self._session:
            self._server = xmlrpclib.Server(self._url)
            self._session = self._server.login(self._user, self._pwd)
            return True
        else:
            raise xmlrpclib.Fault(faultCode=1, faultString="Connection already established!")

    def disconnect(self):
        if self._session:
            return self._server.endSession(self._session)
        else:
            raise xmlrpclib.Fault(faultCode=1, faultString='No connection available!')

    def multi_call(self, data=[]):
        if data and self._session:
            chunks = [data[i:i+self.CALL_CHUNK] for i in range(0, len(data), self.CALL_CHUNK)]
            sync = self
            return map(lambda chunk: sync._server.multiCall(sync._session, chunk), chunks)
        else:
            raise xmlrpclib.Fault(faultCode=1, faultString='No connection available!')
