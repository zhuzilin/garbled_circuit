# Copyright 2021 zhuzilin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""public key based olivious transfer"""
# TODO(zilinzhu) Find a way to use less pickle...
import pickle

import zmq
import rsa


class OTSender:
    def __init__(self, addr, context=None):
        self.context = context or zmq.Context.instance()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(addr)
        self.x0, self.x1 = None, None
        self.started = False

    def start(self, x0, x1):
        if not self.started:
            self.x0, self.x1 = x0, x1
            self.listen()

    def listen(self):
        pub_0 = self._recv()
        pub_1 = self._recv(zmq.RCVMORE)

        enc_x0 = rsa.encrypt(pickle.dumps(self.x0), pub_0)
        enc_x1 = rsa.encrypt(pickle.dumps(self.x1), pub_1)
        self._send(enc_x0, zmq.SNDMORE)
        self._send(enc_x1)
        self.started = False

    def _send(self, data, flag=0):
        self.socket.send(pickle.dumps(data), flag)

    def _recv(self, flag=0):
        return pickle.loads(self.socket.recv(flag))


class OTReceiver:
    def __init__(self, addr, context=None):
        self.context = context or zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(addr)

    def ask_for(self, b: bool):
        (pub_key, priv_key) = rsa.newkeys(512)
        # TODO(zilinzhu) Find a way to create random key without
        # generating private key.
        (fake_key, _) = rsa.newkeys(512)
        if b:
            pubs = (fake_key, pub_key)
        else:
            pubs = (pub_key, fake_key)
        self._send(pubs[0], zmq.SNDMORE)
        self._send(pubs[1])

        enc_x0 = self._recv()
        enc_x1 = self._recv(zmq.RCVMORE)
        encs = (enc_x0, enc_x1)

        res = pickle.loads(rsa.decrypt(encs[b], priv_key))

        return res

    def _send(self, data, flag=0):
        self.socket.send(pickle.dumps(data), flag)

    def _recv(self, flag=0):
        return pickle.loads(self.socket.recv(flag))
