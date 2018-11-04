# Changelog

## 2.3.2

- Fixed: Name calculate error when volume directory name contain
    dot (.).

## 2.3.1

- Fixed: `--help` message error

## 2.3.0

- API change
  - Change: `--input-formats` -&gt; `-e` & `--extractors`
  - Change: `--output-format` -&gt; `-c` & `--compressor`

## 2.2.1

- Fixed unrar password error code == 10 problem.
- Use unrar `x` command to replace the `e` command to avoid the same
  filename in difference sub folders.

## 2.2.0

- Tweak command line interface.

## 2.1.4

- Fix unexpected delete data source when some rare case.

## 2.1.3

- Fix typo in `--help`
- Fix unexpected delete when use `--delete` option.

## 2.1.0

- Support `--output-alldir` to transfer result data to other folder.
- Support `--replace` to decide program should replace old result
  or not.
- Support new extractor `zip` and new compressor `dir`. It make
  reverse operation is possible. (use `--reverse` for shortly.)

## 2.0.0

- Support `rar` format.
