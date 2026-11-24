#!/usr/bin/env python3
"""One-line cat review for the make.fun bounty.

Writes a single deadpan one-star review, written by a house cat about
its human, to <MAKEFUN_OUTPUT_DIR>/entry.txt (default /output).
Pure standard library only.
"""

import os
import stat
import sys
import tempfile

ENTRY = (
    "One star. He spent $200 on a heated bed, then sulked when I slept "
    "on his laptop instead. The laptop was warm first."
)


def validate(text):
    """Validate the entry line: 1-200 chars, single line, clean."""
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not 1 <= len(text) <= 200:
        raise ValueError(f"entry must be 1-200 chars, got {len(text)}")
    if text.strip() != text:
        raise ValueError("entry must not have leading/trailing whitespace")
    if not text.strip():
        raise ValueError("entry must not be whitespace-only")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise ValueError("entry must not contain control characters")
    if not text.startswith("One star"):
        raise ValueError("entry must keep the deadpan one-star review shape")
    # The gate counts characters, so keep the byte length sane too.
    if len(text.encode("utf-8")) > 200:
        raise ValueError("entry must be at most 200 bytes as well")
    return text


def main():
    line = validate(ENTRY)
    data = line.encode("utf-8")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    final_path = os.path.join(out_dir, "entry.txt")

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        os.chmod(tmp_path, 0o644)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, final_path)
        os.chmod(final_path, 0o644)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify: exact bytes, UTF-8, no trailing newline, mode.
    with open(final_path, "rb") as f:
        read_back = f.read()
    if read_back != data:
        raise ValueError("read-back mismatch")
    if read_back.decode("utf-8") != line:
        raise ValueError("read-back UTF-8 mismatch")
    if read_back.endswith(b"\n"):
        raise ValueError("output must not end with a newline")
    mode = stat.S_IMODE(os.stat(final_path).st_mode)
    if mode != 0o644:
        raise ValueError(f"output mode must be 0644, got {oct(mode)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
