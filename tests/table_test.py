import sys
import os
import pytest

path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '..', r'extdict'
    )
)
sys.path.insert(0, path)
with open(".env", "w+") as env:
    python_path = r"PYTHONPATH="+f'"{path}"'
    if env.read() != python_path:
        env.write(python_path)

from table import Table

example_table: Table | None = None

def test_initiation():
    global example_table
    example_table = Table(
        content=dict([(n, n) for n in range(0, 10)]),
        read_only_indices={n for n in range(0, 5)}, minimum_size=7,
        maximum_size=12
    )

def test_size_setting():
    global example_table
    with pytest.raises(TypeError):
        example_table.minimum_size = "hi"
    with pytest.raises(ValueError):
        example_table.minimum_size = 12
    with pytest.raises(ValueError):
        example_table.minimum_size = -1
    example_table.minimum_size = 10
    assert example_table.minimum_size == 10
    with pytest.raises(TypeError):
        example_table.maximum_size = "hi"
    with pytest.raises(ValueError):
        example_table.maximum_size = 9
    example_table.maximum_size = 10
    assert example_table.maximum_size == 10

def test_size_constraints():
    global example_table
    with pytest.raises(KeyError):
        example_table[10] = 10
    with pytest.raises(KeyError):
        example_table += Table({10: 10})
    with pytest.raises(KeyError):
        example_table = example_table + Table({10: 10})
    with pytest.raises(KeyError):
        example_table[9] = None
    with pytest.raises(KeyError):
        example_table -= Table({9: 9})
    with pytest.raises(KeyError):
        example_table = example_table - Table({9: 9})
    
def test_arithmetic():
    global example_table
    example_table.maximum_size = 11
    example_table += Table({10: 10})
    example_table -= Table({10: 10})
    new_table = example_table + Table({10: 10})
    new_table = new_table - Table({10: 10})
    assert new_table == example_table
    assert example_table + Table({10: 10}) != new_table
    
def test_read_only():
    global example_table
    assert 0 in example_table.read_only_indices
    with pytest.raises(KeyError):
        example_table[0] = 1
    example_table.read_only_indices.remove(0)
    example_table[0] = 1
    example_table.read_only_indices.add(0)
    with pytest.raises(KeyError):
        example_table[0] = 0
    assert tuple(example_table.read_only_indices) == example_table.get_indices(
        read_only_specifier="read only"
    )

def test_cloning():
    base_table = Table({1: "d"})
    other_table = Table({1: "e"})
    base_table[0] = other_table
    other_table[0] = base_table
    new_table = base_table.clone()
    new_table[1] = "a"
    other_table[1] = "b"
    base_table[1] = "c"
    assert new_table[1] == "a"
    assert other_table[1] == "b"
    assert base_table[1] == "c"
    assert new_table[0][1] == "e"
    assert new_table[0][0][1] == "a"
    assert base_table[0][0][1] == "c"

def test_find_index():
    new_table = Table({1: 0, 2: 0, 3: 0, 4: 1}, {1, 2})
    assert (1, 2) == new_table.find_index(
        value=0, read_only_specifier="read only"
    )
    assert (3,) == new_table.find_index(
        value=0, read_only_specifier="exclude read only"
    )
    assert (1,) == new_table.find_index(
        value=0, maximum_amount=1, read_only_specifier="read only"
    )
    assert (1, 2, 3) == new_table.find_index(value=0)
    assert (1, 2) == new_table.find_index(value=0, maximum_amount=2)
    with pytest.raises(ValueError):
        new_table.find_index(value=0, maximum_amount=0)
    with pytest.raises(TypeError):
        new_table.find_index(value=0, maximum_amount="0")
    assert () == new_table.find_index(
        value=1, read_only_specifier="read only"
    )

def test_get_methods():
    new_table = Table({1: 0, 2: 0, 3: 0, 4: 1}, {1, 2})
    assert (0, 0) == new_table.get_values(read_only_specifier="read only")
    assert (0, 1) == new_table.get_values(
        read_only_specifier="exclude read only"
    )
    assert (0, 0) == new_table.get_values(maximum_amount=2)
    with pytest.raises(TypeError):
        new_table.get_values(maximum_amount="0")
    with pytest.raises(ValueError):
        new_table.get_values(maximum_amount=-1)
    assert ((1, 0), (2, 0), (3, 0), (4, 1)) == new_table.get_pairs()
    assert ((1, 0),) == new_table.get_pairs(
        maximum_amount=1, read_only_specifier="read only"
    )
    assert ((3, 0), (4, 1)) == new_table.get_pairs(
        maximum_amount=4, read_only_specifier="exclude read only"
    )
    with pytest.raises(ValueError):
        new_table.get_pairs(maximum_amount=0)
    with pytest.raises(TypeError):
        new_table.get_pairs(maximum_amount="0")