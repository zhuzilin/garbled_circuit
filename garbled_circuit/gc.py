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

from copy import deepcopy
from enum import Enum
import hashlib
import pickle
import random

import zmq

from .basic_types import Int, PlaceHolder
from .circuit import Circuit
from .ot import OTSender, OTReceiver


class Role(Enum):
    # The player who will generate the random numbers
    SENDER = "SENDER"
    RECEIVER = "RECEIVER"


def generate_k_pair(K):
    k0 = random.randint(0, 1 << K - 1)
    k1 = random.randint(0, 1 << K - 1)
    while k1 == k0:
        k1 = random.randint(0, 1 << K - 1)
    p0 = random.randint(0, 1)
    p1 = 1 - p0
    return (k0, p0), (k1, p1)


def sha256(s):
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)


class GarbledCircuit(Circuit):
    def __init__(self, circuit, role, addr, ot_addr, context=None):
        gates = deepcopy(circuit.gates)
        super().__init__(
            gates, circuit.input_sizes, circuit.output_sizes, circuit.num_wire
        )
        self.role = role
        self.context = context or zmq.Context.instance()
        if self.role == Role.SENDER:
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(addr)
            self.ot = OTSender(ot_addr)
        else:
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(addr)
            self.ot = OTReceiver(ot_addr)

    def __call__(self, inputs):
        assert len(inputs) == self.num_input

        if self.role == Role.SENDER:
            # key
            K = 32
            k = []
            for i in range(self.num_wire):
                k.append(generate_k_pair(K))

            garbled_table = self.create_garbled_table(k)
            decoding_table = self.create_decoding_table(k)

            self._send(garbled_table, zmq.SNDMORE)
            self._send(decoding_table)
            self._recv()
        else:
            garbled_table = self._recv()
            decoding_table = self._recv(zmq.SNDMORE)
            self._send("")

        print("Finish send/recv garbled table and decoding table.")

        # The encrypted value of wires.
        if self.role == Role.RECEIVER:
            enc_wires = [None] * self.num_wire
        wire_idx = 0
        for i in range(self.num_input):
            if isinstance(inputs[i], PlaceHolder):
                for j in range(self.input_sizes[i]):
                    if self.role == Role.SENDER:
                        self.ot.start(x0=k[wire_idx][0], x1=k[wire_idx][1])
                    else:
                        flag = zmq.RCVMORE if j != 0 else 0
                        enc_wires[wire_idx] = self._recv(flag=flag)
                    wire_idx += 1
                if self.role == Role.RECEIVER:
                    self._send("")
            else:
                for j in range(self.input_sizes[i]):
                    if self.role == Role.SENDER:
                        flag = zmq.SNDMORE if j != self.input_sizes[i] - 1 else 0
                        self._send(k[wire_idx][inputs[i].digit(j)], flag=flag)
                    else:
                        enc_wires[wire_idx] = self.ot.ask_for(b=inputs[i].digit(j))
                    wire_idx += 1
                if self.role == Role.SENDER:
                    self._recv()

        print("Finish send/recv encoded inputs.")

        if self.role == Role.RECEIVER:
            for i in range(self.num_gate):
                gate = self.gates[i]
                if len(gate.input_wires) == 2:
                    a, b = gate.input_wires
                    c = gate.output_wires[0]
                    k_a, p_a = enc_wires[a]
                    k_b, p_b = enc_wires[b]
                    e = garbled_table[(i, p_a, p_b)]
                    w_c = e ^ sha256(str(k_a) + str(k_b) + str(i))
                    k_c, p_c = w_c >> 1, w_c & 1
                    enc_wires[c] = (k_c, p_c)
                elif len(gate.input_wires) == 1:
                    a = gate.input_wires[0]
                    c = gate.output_wires[0]
                    k_a, p_a = enc_wires[a]
                    e = garbled_table[(i, p_a, p_b)]
                    w_c = e ^ sha256(str(k_a) + str(i))
                    k_c, p_c = w_c >> 1, w_c & 1
                    enc_wires[c] = (k_c, p_c)
                else:
                    raise ValueError(
                        f"Does not support gate with inputs more than 2. Got {gate.num_input}."
                    )
            # Decoding
            outputs = []
            offset = self.output_offset
            for i in range(self.num_output):
                output_bits = []
                for j in range(self.output_sizes[i]):
                    k_v, p_v = enc_wires[offset]
                    e = decoding_table[(offset, p_v)]
                    v = e ^ sha256(str(k_v) + "out" + str(offset))
                    assert v == 0 or v == 1
                    output_bits.append(bool(v))
                    offset += 1
                outputs.append(Int.from_bits(output_bits))
            self._recv()
            self._send(outputs)
        else:
            self._send("")
            outputs = self._recv()

        return outputs

    def create_garbled_table(self, k):
        garbled_table = {}
        for i in range(self.num_gate):
            gate = self.gates[i]
            # TODO(zilinzhu) Adapt to gate of inputs larger than 2.
            if gate.num_input > 2:
                continue
            if gate.num_input == 2:
                a, b = gate.input_wires
                c = gate.output_wires[0]
                for v_a in [0, 1]:
                    k_v_a, p_v_a = k[a][v_a]
                    for v_b in [0, 1]:
                        k_v_b, p_v_b = k[b][v_b]

                        v_c = gate([bool(v_a), bool(v_b)])[0]
                        k_v_c, p_v_c = k[c][v_c]
                        w_c = k_v_c << 1 | p_v_c
                        # TODO(zilinzhu) The concatenate here seems wrong...
                        # Need to double check the algorithm.
                        h = sha256(str(k_v_a) + str(k_v_b) + str(i))
                        e = h ^ w_c
                        assert e ^ h == w_c
                        garbled_table[(i, p_v_a, p_v_b)] = e
            elif gate.num_input == 1:
                a = gate.input_wires[0]
                c = gate.output_wires[0]
                for v_a in [0, 1]:
                    k_v_a, p_v_a = k[a][v_a]

                    v_c = gate([bool(v_a)])[0]
                    k_v_c, p_v_c = k[c][v_c]
                    w_c = k_v_c << 1 | p_v_c
                    # TODO(zilinzhu) The concatenate here seems wrong...
                    # Need to double check the algorithm.
                    h = sha256(str(k_v_a) + str(i))

                    e = h ^ w_c
                    garbled_table[(i, p_v_a)] = e
            else:
                raise ValueError(
                    f"Does not support gate with inputs more than 2. Got {gate.num_input}."
                )
        return garbled_table

    def create_decoding_table(self, k):
        decoding_table = {}
        offset = self.output_offset
        for i in range(self.num_output):
            for _ in range(self.output_sizes[i]):
                for v in [0, 1]:
                    k_v, p_v = k[offset][v]
                    # Here the last bit should be the index of
                    # the gate which is responsible to the output.
                    e = sha256(str(k_v) + "out" + str(offset)) ^ v
                    decoding_table[(offset, p_v)] = e
                offset += 1
        return decoding_table

    def _send(self, data, flag=0):
        self.socket.send(pickle.dumps(data), flag)

    def _recv(self, flag=0):
        return pickle.loads(self.socket.recv(flag))
