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

from garbled_circuit.basic_types import Int, PlaceHolder
from garbled_circuit.gc import GarbledCircuit, Role
from garbled_circuit.parser import parse


def read_circuit_from_file(filename):
    with open(filename) as f:
        s = f.read()
    circuit = parse(s)
    return circuit


filename = "circuit/basic/mult64.txt"
# filename = "and-4.txt"
circuit = read_circuit_from_file(filename)

inputs = [PlaceHolder(), Int(201)]
assert circuit.num_input == len(inputs)

p2 = GarbledCircuit(
    circuit, role=Role.RECEIVER, addr="tcp://*:5004", ot_addr="tcp://127.0.0.1:5005"
)

outputs = p2(inputs)

print(outputs[0])
