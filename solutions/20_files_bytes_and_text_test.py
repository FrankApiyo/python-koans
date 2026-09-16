"""Files, bytes, and text.

open(path) does not give you the contents of a file. It gives you a file
object: a cursor into the file that remembers where it is. read() returns
everything from the cursor to the end and leaves the cursor there, so a
second read() returns nothing. read(n) returns at most n items and moves
the cursor past them; the last piece is short, and after that read()
returns an empty value. That empty value is how you know you are done.

    with open(path) as handle:
        handle.read(3)       # "abc"
        handle.read(3)       # "d", the last piece is short
        handle.read(3)       # "", nothing left

The mode decides what kind of value you get. "r" is text mode: bytes on
disk are decoded with an encoding, your locale's unless you pass
encoding=, which is why portable code always passes it, and you get str.
"rb" is binary mode: you get the raw bytes and no decoding happens. Text
mode with the wrong encoding raises UnicodeDecodeError. tell() reports the
cursor and seek(0) moves it back to the start. In binary mode they are byte
offsets; in text mode tell() is an opaque bookmark and seek() accepts only
0 or a value tell() gave you.

A file object is also an iterator (chapter 08). readline() returns one
line including its newline, and a for loop over the handle yields one
line at a time without loading the rest, so a file of any size can be
processed in constant memory. io.StringIO and io.BytesIO are file objects
that live in memory, useful for tests and for anything written against
file objects. with (chapter 09) closes the file on the way out, and a
closed file refuses to be read.

This chapter has no diagram; the lesson is on lessons/index.html too.
"""

import io

import pytest

from conftest import __


def chunks(handle, size):
    while True:
        piece = handle.read(size)
        if not piece:
            return
        yield piece


def count_lines(path):
    with open(path) as handle:
        return sum(1 for _ in handle)


def test_open_returns_a_cursor_not_the_contents(tmp_path):
    """read() hands over everything from the cursor to the end and leaves the cursor there. Ask again and there is nothing left to give."""
    path = tmp_path / "note.txt"
    path.write_text("hello")
    with open(path) as handle:
        assert handle.read() == "hello"
        assert handle.read() == ""


def test_text_mode_gives_str_and_binary_mode_gives_bytes(tmp_path):
    """The bytes on disk are the same either way. "r" decodes them into a str; "rb" hands them over untouched."""
    path = tmp_path / "note.txt"
    path.write_text("hi")
    with open(path) as text:
        assert text.read() == "hi"
    with open(path, "rb") as binary:
        assert binary.read() == b"hi"


def test_read_n_takes_at_most_n_and_the_last_piece_is_short(tmp_path):
    """Seven characters read three at a time come out as 3, 3, 1. The empty string after that is the signal to stop, not an error."""
    path = tmp_path / "note.txt"
    path.write_text("abcdefg")
    with open(path) as handle:
        assert handle.read(3) == "abc"
        assert handle.read(3) == "def"
        assert handle.read(3) == "g"
        assert handle.read(3) == ""


def test_chunks_streams_a_file_a_piece_at_a_time(tmp_path):
    """Implement chunks above. 1. Loop forever: read size items from handle into a local variable. 2. If that value is empty, return, which ends the generator. 3. Otherwise yield it. Nothing larger than one piece is ever in memory, and the same code serves text and bytes."""
    path = tmp_path / "note.txt"
    path.write_text("abcdefg")
    with open(path) as handle:
        assert list(chunks(handle, 3)) == ["abc", "def", "g"]
    with open(path, "rb") as handle:
        assert list(chunks(handle, 4)) == [b"abcd", b"efg"]
    with open(path) as handle:
        assert list(chunks(handle, 100)) == ["abcdefg"]


def test_readline_keeps_the_newline_and_iteration_continues_from_there(tmp_path):
    """readline() stops just after the first newline and includes it. The handle is an iterator, so a loop picks up wherever the cursor is."""
    path = tmp_path / "note.txt"
    path.write_text("one\ntwo\nthree")
    with open(path) as handle:
        assert handle.readline() == "one\n"
        assert list(handle) == ["two\n", "three"]


def test_count_lines_never_holds_the_whole_file(tmp_path):
    """Implement count_lines above. 1. Open path in a with statement. 2. Return sum(1 for _ in handle): the loop pulls one line at a time, so a file with millions of lines costs the same memory as one with ten."""
    path = tmp_path / "big.txt"
    path.write_text("".join(f"line {n}\n" for n in range(10_000)))
    assert count_lines(path) == 10_000
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    assert count_lines(empty) == 0


def test_tell_reports_the_cursor_and_seek_moves_it(tmp_path):
    """Both count bytes from the start of the file. Reading two bytes leaves the cursor at 2; seek(0) rewinds so the same bytes can be read again."""
    path = tmp_path / "note.txt"
    path.write_bytes(b"abcdef")
    with open(path, "rb") as handle:
        handle.read(2)
        assert handle.tell() == 2
        handle.seek(0)
        assert handle.read(2) == b"ab"


def test_an_encoding_turns_bytes_into_text_and_the_wrong_one_fails(tmp_path):
    """One character can be several bytes: café is four characters and five bytes in utf-8. Decoding those bytes as ascii cannot work, and Python says so instead of guessing."""
    path = tmp_path / "note.txt"
    path.write_bytes("café".encode("utf-8"))
    with open(path, encoding="utf-8") as handle:
        assert len(handle.read()) == 4
    assert len(path.read_bytes()) == 5
    with pytest.raises(UnicodeDecodeError):
        with open(path, encoding="ascii") as handle:
            handle.read()


def test_stringio_and_bytesio_are_files_that_live_in_memory():
    """They answer to read, readline, seek and tell like a file on disk, so code written for file objects runs on them unchanged. getvalue() shows everything written so far."""
    text = io.StringIO("a\nb")
    assert text.readline() == "a\n"
    binary = io.BytesIO(b"xyz")
    assert binary.read(2) == b"xy"
    out = io.StringIO()
    out.write("hello")
    assert out.getvalue() == "hello"


def test_with_closes_the_file_even_when_the_block_raises(tmp_path):
    """The file object is a context manager from chapter 09. Its __exit__ calls close, so the closed flag flips on the way out, and a closed file refuses to read rather than returning stale data."""
    path = tmp_path / "note.txt"
    path.write_text("hello")
    with pytest.raises(RuntimeError):
        with open(path) as handle:
            assert handle.closed is False
            raise RuntimeError("boom")
    assert handle.closed is True
    with pytest.raises(ValueError):
        handle.read()
