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
    - p: |
        q
        r
        s
l: b
m:
  - h: i
    j: k
n: 2
o: "2"
p:
  d: e
  f: 2
  g: 3
  h: 5
"""
sample_output_raw = """
a: &label0000 "b"
c: &label0001
  d: "e"
  f: &label0002 2
  g:
    - &label0003
      h: "i"
      j: &label0004 "k"
    - l: "m"
    - *label0003
    - j: *label0004
    - p: |
        q
        r
        s
l: *label0000
m:
  - *label0003
n: *label0002
o: "2"
p:
  <<: *label0001
  g: 3
  h: 5
"""


def test_dumps():
    sample_input = parse(sample_input_raw)
    sample_output = parse(sample_output_raw)
    assert sample_input == sample_output
    assert dumps(sample_input).strip() == sample_output_raw.strip()
    assert parse(dumps(sample_input)) == sample_output
