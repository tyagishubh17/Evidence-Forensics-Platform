"""Unit tests for SHA-256 hashing and integrity verification (app/integrity.py)."""
import hashlib

from app.integrity import (TAMPER_MARKER, calculate_sha256, create_tampered_copy,
                           verify_integrity)

# Published SHA-256 test vectors (FIPS 180-2 / NIST).
SHA256_OF_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
SHA256_OF_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def write_file(path, content):
    path.write_bytes(content)
    return str(path)


def test_hash_matches_known_test_vector(tmp_path):
    assert calculate_sha256(write_file(tmp_path / "abc.txt", b"abc")) == SHA256_OF_ABC


def test_hash_of_empty_file(tmp_path):
    assert calculate_sha256(write_file(tmp_path / "empty.txt", b"")) == SHA256_OF_EMPTY


def test_hash_is_64_lowercase_hex_characters(tmp_path):
    digest = calculate_sha256(write_file(tmp_path / "a.txt", b"synthetic evidence"))
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_large_file_is_hashed_correctly_in_chunks(tmp_path):
    # About 1.3 MB, so the file is read in many 64 KB chunks.
    data = bytes(range(256)) * 5000
    path = write_file(tmp_path / "large.bin", data)
    assert calculate_sha256(path) == hashlib.sha256(data).hexdigest()


def test_one_byte_change_gives_a_different_hash(tmp_path):
    first = calculate_sha256(write_file(tmp_path / "a.txt", b"Case note version 1"))
    second = calculate_sha256(write_file(tmp_path / "b.txt", b"Case note version 2"))
    assert first != second


def test_verify_unchanged_file_returns_match(tmp_path):
    path = write_file(tmp_path / "note.txt", b"synthetic note")
    recorded = calculate_sha256(path)
    result = verify_integrity(path, recorded)
    assert result["status"] == "MATCH"
    assert result["current_hash"] == recorded


def test_verify_accepts_uppercase_recorded_hash(tmp_path):
    path = write_file(tmp_path / "note.txt", b"abc")
    assert verify_integrity(path, SHA256_OF_ABC.upper())["status"] == "MATCH"


def test_verify_modified_file_returns_mismatch(tmp_path):
    path = write_file(tmp_path / "note.txt", b"synthetic note")
    recorded = calculate_sha256(path)
    write_file(tmp_path / "note.txt", b"synthetic note - edited")  # test file only
    result = verify_integrity(path, recorded)
    assert result["status"] == "MISMATCH"
    assert result["current_hash"] != recorded


def test_verify_missing_file_returns_missing(tmp_path):
    result = verify_integrity(str(tmp_path / "does-not-exist.txt"), SHA256_OF_ABC)
    assert result["status"] == "MISSING"
    assert result["current_hash"] is None


def test_tampered_copy_is_detected_and_original_is_unchanged(tmp_path):
    original_bytes = b"%PDF-1.4 synthetic sample content"
    original = write_file(tmp_path / "original.pdf", original_bytes)
    recorded = calculate_sha256(original)

    copy_path = create_tampered_copy(original, str(tmp_path / "copies"), "copy.pdf")

    # The copy lives in the separate folder and contains the marker.
    assert copy_path.startswith(str(tmp_path / "copies"))
    assert open(copy_path, "rb").read() == original_bytes + TAMPER_MARKER

    # The copy no longer matches; the original still does, byte for byte.
    assert verify_integrity(copy_path, recorded)["status"] == "MISMATCH"
    assert verify_integrity(original, recorded)["status"] == "MATCH"
    assert open(original, "rb").read() == original_bytes
