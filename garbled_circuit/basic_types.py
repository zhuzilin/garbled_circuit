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
import numpy as np


def get_np_int_func(num_digit):
    assert (
        num_digit & (num_digit - 1) == 0 and 8 <= num_digit <= 64
    ), "num_digit should be 2^n in [8, 64]"
    if num_digit == 8:
        return np.int8
    elif num_digit == 16:
        return np.int16
    elif num_digit == 32:
        return np.int32
    elif num_digit == 64:
        return np.int64


# A Int64 type
class Int:
    def __init__(self, val: int, num_digit=64):
        self.f = get_np_int_func(num_digit)
        self.val = self.f(val)

    def __str__(self):
        return f"Int({self.val})"

    def digit(self, i) -> bool:
        return bool(self.val & (self.f(1) << i))

    @staticmethod
    def from_bits(bits: List[bool], num_digit=64):
        f = get_np_int_func(num_digit)
        val = f(0)
        for bit in bits[::-1]:
            val <<= 1
            if bit:
                val |= 1
        return Int(val, num_digit)


# The input that the current player don't possess.
class PlaceHolder:
    def __init__(self):
        pass
