## garbled_circuit

This is a python implementation of Yao's GC.

### Usage

I choose the [Bristol Format](https://homes.esat.kuleuven.be/~nsmart/MPC/) to represent the circuit, which is a standard format adopted by many tools and libraries. Some examples of the format can be found in the `circuit/basic` folder. All the circuit files are downloaded from [here](https://homes.esat.kuleuven.be/~nsmart/MPC/).

You can use the `parse` function in `garbled_circuit.parser` to get the `Circuit` structure:

```python
from garbled_circuit.parser import parse

def read_circuit_from_file(filename):
    with open(filename) as f:
        s = f.read()
    circuit = parse(s)
    return circuit


filename = "circuit/basic/mult64.txt"
circuit = read_circuit_from_file(filename)
```

And for the 2 players in the MPC, I call the one who creates and sends the garbled_table and decoding table `SENDER` and the other one who will receive them `RECEIVER`. You could use the following way to do a integer multiplication with Yao's GC (which used the `mult64.txt` file above).

-  **Sender**

```python
from garbled_circuit.basic_types import Int, PlaceHolder
from garbled_circuit.gc import GarbledCircuit, Role

inputs = [Int(15), PlaceHolder()]

p1 = GarbledCircuit(
    circuit, role=Role.SENDER, addr="tcp://127.0.0.1:5004", ot_addr="tcp://*:5005"
)

outputs = p1(inputs)
```

- **Receiver**

```python
from garbled_circuit.basic_types import Int, PlaceHolder
from garbled_circuit.gc import GarbledCircuit, Role

inputs = [PlaceHolder(), Int(20)]

p2 = GarbledCircuit(
    circuit, role=Role.RECEIVER, addr="tcp://*:5004", ot_addr="tcp://127.0.0.1:5005"
)

outputs = p2(inputs)
```

And both player will get output `300`.
