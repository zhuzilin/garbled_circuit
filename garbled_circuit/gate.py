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

from .operation import Operation


class Gate:
    def __init__(self, operation, input_wires, output_wires):
        self.operation = operation
        self.input_wires = input_wires
        self.output_wires = output_wires

    @property
    def num_input(self):
        return len(self.input_wires)

    @property
    def num_output(self):
        return len(self.output_wires)

    def __call__(self, inputs: List[bool]):
        assert len(inputs) == self.num_input
        if self.operation == Operation.XOR:
            return [inputs[0] != inputs[1]]
        elif self.operation == Operation.AND:
            return [inputs[0] and inputs[1]]
        elif self.operation == Operation.NOT:
            return [not inputs[0]]
        elif self.operation == Operation.EQ:
            raise NotImplementedError("EQ not implemented yet.")
        elif self.operation == Operation.EQW:
            raise NotImplementedError("EQW not implemented yet.")
        elif self.operation == Operation.MAND:
            raise NotImplementedError("MAND not implemented yet.")
        else:
            raise ValueError(f"Unknown operation type: {self.operation}")
