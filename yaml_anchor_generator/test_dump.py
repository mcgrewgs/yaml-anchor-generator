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
    d: 7
n: 2
o: "2"
p:
  d: e
  f: 2
  g: 3
  h: 5
"""
sample_output_raw = """
a: &label_a "b"
c: &label_c
  d: "e"
  f: &label_c_f 2
  g:
    - &label_c_g_0
      h: "i"
      j: &label_c_g_0_j "k"
    - l: "m"
    - *label_c_g_0
    - j: *label_c_g_0_j
    - p: |
        q
        r
        s
l: *label_a
m:
  - <<: *label_c_g_0
    d: 7
n: *label_c_f
o: "2"
p:
  <<: *label_c
  g: 3
  h: 5
"""


def test_dumps() -> None:
    sample_input = parse(sample_input_raw)
    sample_output = parse(sample_output_raw)
    assert sample_input == sample_output
    assert dumps(sample_input).strip() == sample_output_raw.strip()
    assert parse(dumps(sample_input)) == sample_output
