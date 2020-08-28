# YAML Anchor Generator

Analyze an existing input YAML file, and output one that makes use of anchors and labels to cut down on repetition.

I didn't quickly find an existing project that does this, so here we are.

# Running

```shell
[root@localhost]$ ./run.sh
[root@localhost]$ ./run.sh your_input_yaml_filename_here.yml
[root@localhost]$ ./run.sh your_input_yaml_filename_here.yml your_output_yaml_filename_here.yml
```

# Current State

Works for duplicated strings (even multi-line)

Merges dictionaries together

# Future Work

Merge lists?
