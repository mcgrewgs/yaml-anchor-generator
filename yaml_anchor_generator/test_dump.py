from yaml_anchor_generator.dump import dumps
from yaml import full_load as parse

sample_input_raw = """
a: b
c:
  d: e
  f: 2
  g:
    - h: i
      j: k
    - l: m
    - h: i
      j: k
    - j: k
l: b
m:
  - h: i
    j: k
n: 2
o: "2"
"""
sample_output_raw = """
a: &label0000 "b"
c:
  d: "e"
  f: &label0001 2
  g:
    - &label0002
      h: "i"
      j: &label0003 "k"
    - l: "m"
    - *label0002
    - j: *label0003
l: *label0000
m:
  - *label0002
n: *label0001
o: "2"
"""


def test_dumps():
    sample_input = parse(sample_input_raw)
    sample_output = parse(sample_output_raw)
    assert sample_input == sample_output
    assert dumps(sample_input).strip() == sample_output_raw.strip()
    assert parse(dumps(sample_input)) == sample_output
