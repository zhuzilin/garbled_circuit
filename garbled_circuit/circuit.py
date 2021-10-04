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

from typing import List

from .basic_types import Int
from .gate import Gate


class Circuit:
    def __init__(self, gates: List[Gate], input_sizes, output_sizes, num_wire):
        self.gates = gates
        self.input_sizes = input_sizes
        self.output_sizes = output_sizes
        self.num_wire = num_wire
        self.output_offset = num_wire - sum(output_sizes)

    @property
    def num_gate(self):
        return len(self.gates)

    @property
    def num_input(self):
        return len(self.input_sizes)

    @property
    def num_output(self):
        return len(self.output_sizes)

    def __call__(self, inputs: Int):
        assert len(inputs) == self.num_input
        wires = [None] * self.num_wire
        wire_idx = 0
        for i in range(self.num_input):
            for j in range(self.input_sizes[i]):
                wires[wire_idx] = inputs[i].digit(j)
                wire_idx += 1

        for gate in self.gates:
            input_wires = [wires[i] for i in gate.input_wires]
            output_wires = gate(input_wires)
            assert len(output_wires) == gate.num_output
            for i in range(gate.num_output):
                wires[gate.output_wires[i]] = output_wires[i]

        outputs = []
        offset = self.output_offset
        for i in range(self.num_output):
            outputs.append(Int.from_bits(wires[offset : offset + self.output_sizes[i]]))
            offset += self.output_sizes[i]
        return outputs
