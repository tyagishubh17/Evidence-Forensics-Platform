"""
Evidence integrity functions: SHA-256 hashing, verification and the
controlled tamper-detection demonstration.

These functions have no Flask dependency, so they are easy to unit test.
"""
import hashlib
import os
import shutil

# Files are read in 64 KB pieces so large files do not need to fit in memory.
CHUNK_SIZE = 64 * 1024

# Text appended to the *copy* during the tamper demonstration.
TAMPER_MARKER = b"\n[TAMPER TEST] This line was added to a copy to simulate modification.\n"


def calculate_sha256(file_path):
    """Return the SHA-256 hash of a file as a 64-character hexadecimal string."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_integrity(file_path, recorded_hash):
    """
    Recalculate the hash of a file and compare it with the recorded hash.

    Returns a dictionary with:
        status        -- "MATCH", "MISMATCH" or "MISSING" (file not found)
        recorded_hash -- the hash stored at upload time
        current_hash  -- the hash calculated now (None if the file is missing)
    """
    recorded_hash = recorded_hash.lower()

    if not os.path.isfile(file_path):
        return {"status": "MISSING", "recorded_hash": recorded_hash, "current_hash": None}

    current_hash = calculate_sha256(file_path)
    status = "MATCH" if current_hash == recorded_hash else "MISMATCH"
    return {"status": status, "recorded_hash": recorded_hash, "current_hash": current_hash}


def create_tampered_copy(original_path, copy_folder, copy_filename):
    """
    Copy the original file into a separate folder, then modify ONLY the copy
    by appending a short marker. The original file is opened read-only and is
    never changed.

    Returns the path of the modified copy.
    """
    os.makedirs(copy_folder, exist_ok=True)
    copy_path = os.path.join(copy_folder, copy_filename)

    shutil.copyfile(original_path, copy_path)
    with open(copy_path, "ab") as copy_file:
        copy_file.write(TAMPER_MARKER)

    return copy_path
