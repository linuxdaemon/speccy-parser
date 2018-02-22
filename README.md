# speccy-parser
A basic library for parsing information from a Speccy snapshot

## Basic Usage

```python
>>> from speccyparse import parse
>>> data = parse(speccy_id)
>>> data["Summary"]["Operating System"]
'Windows 10 Pro 64-bit'
```
