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

import logging

from .circuit import Circuit
from .gate import Gate
from .operation import str2operation, Operation


def s2lines(s):
    lines = s.split("\n")
    lines = [line.strip() for line in lines]
    return list(filter(lambda x: x != "", lines))


def line2ints(line):
    words = line.split()
    return [int(word) for word in words]


# Bristol fashion has the following format:
# <GATE COUNT> <WIRE_COUNT>
# <INPUT COUNT> <FIRST INPUT BIT SIZE> <SECOND INPUT BIT SIZE> ...
# <OUTPUT COUNT> <FIRST OUTPUT SIZE> <SECOND OUTPUT SIZE> ...
# <empty line>
# <GATE INPUT COUNT> <GATE OUTPUT COUNT> <INPUT WIRE INDEX> ... <OUTPUT WIRE INDEX> ... <GATE OPERATION>
def parse(s):
    lines = s2lines(s)
    assert len(lines) > 3

    num_gate, num_wire = line2ints(lines[0])
    input_info = line2ints(lines[1])
    num_input = input_info[0]
    input_sizes = input_info[1:]
    assert len(input_sizes) == num_input

    output_info = line2ints(lines[2])
    num_output = output_info[0]
    output_sizes = output_info[1:]
    assert len(output_sizes) == num_output

    gates = []
    for line in lines[3:]:
        # The last elements of gate info is the operation type,
        # which cannot be casted to integer.
        gate_info = line.split()
        operation = str2operation(gate_info[-1])
        # Remove the tail operation from the gate_info for convenient.
        gate_info = [int(word) for word in gate_info[:-1]]
        num_input_wire, num_output_wire = gate_info[0], gate_info[1]
        if operation == Operation.MAND:
            logging.debug("Extended Bristol Fashion circuit found.")
            assert num_input_wire == 2 * num_output_wire
        if operation != Operation.MAND:
            assert num_input_wire == 1 or num_input_wire == 2
            assert num_output_wire == 1
        assert len(gate_info) == 2 + num_input_wire + num_output_wire
        input_wires = []
        output_wires = []
        for i in range(2, 2 + num_input_wire):
            input_wires.append(gate_info[i])
        for i in range(2 + num_input_wire, 2 + num_input_wire + num_output_wire):
            output_wires.append(gate_info[i])
        gate = Gate(operation, input_wires, output_wires)
        gates.append(gate)

    assert len(gates) == num_gate

    circuit = Circuit(gates, input_sizes, output_sizes, num_wire)

    return circuit
