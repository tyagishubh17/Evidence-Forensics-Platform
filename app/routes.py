"""
Routes for the EPICS Digital Evidence Platform.

Includes:
    - User Authentication: Login, logout, investigator identity switching
    - Dashboard: Key metrics, case overview, quick upload, and live forensic audit feed
    - Cases: Case listing, creation, and detailed case dossiers with linked evidence
    - Evidence: File upload, SHA-256 hash generation, content preview (TXT/Images)
    - Integrity: Verification (MATCH/MISMATCH) and controlled tamper-detection demonstration
    - Forensic Audit Trail: Activity logging of every critical operation
"""
import functools
import os
import uuid
from datetime import datetime, timezone

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for, send_from_directory)

from app.db import (
    add_evidence, authenticate_user, create_case, delete_evidence, get_case, get_dashboard_stats,
    get_evidence, get_user_by_email, get_user_by_id, list_cases, list_recent_activity,
    list_recent_evidence, list_users, log_activity, update_case_status
)
from app.integrity import calculate_sha256, create_tampered_copy, verify_integrity

bp = Blueprint("main", __name__)

FILE_TYPES = {
    "pdf": ("PDF document", "application/pdf"),
    "doc": ("Word document (.doc)", "application/msword"),
    "docx": ("Word document (.docx)", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "jpg": ("JPEG image", "image/jpeg"),
    "jpeg": ("JPEG image", "image/jpeg"),
    "png": ("PNG image", "image/png"),
    "txt": ("Plain text", "text/plain"),
}

FILE_SIGNATURES = {
    "pdf": b"%PDF-",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
    "doc": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",  # Compound File Binary (OLE2)
    "docx": b"PK\x03\x04",  # Office Open XML Zip Header
}


# ---------------------------------------------------------------- helpers

def get_current_user():
    """Return active user from session, or None if not logged in."""
    user_id = session.get("user_id")
    if user_id:
        return get_user_by_id(user_id)
    return None


def login_required(view):
    """View decorator that redirects unauthenticated visitors to /login."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if get_current_user() is None:
            flash("Authentication required. Please sign in to access the platform.", "error")
            return redirect(url_for("main.login"))
        return view(**kwargs)
    return wrapped_view


@bp.app_context_processor
def inject_user():
    """Make current user available to all templates."""
    return {"current_user": get_current_user()}


def get_extension(filename):
    """Return lower-case extension without the dot ('' if none)."""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def clean_display_name(filename):
    """Sanitize original filename for display purposes only."""
    name = filename.replace("\\", "/").split("/")[-1].strip()
    return name[:255] or "unnamed"


def get_upload_size(file_storage):
    """Return size of uploaded file in bytes without saving it."""
    stream = file_storage.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    return size


def content_matches_extension(first_bytes, extension):
    """Verify magic bytes match the file extension."""
    if extension == "txt":
        return b"\x00" not in first_bytes
    return first_bytes.startswith(FILE_SIGNATURES[extension])


@bp.app_template_filter("filesize")
def format_file_size(size_in_bytes):
    """Format file size in human-readable units."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    return f"{size_in_bytes / (1024 * 1024):.2f} MB"


def evidence_path(record):
    return os.path.join(current_app.config["UPLOAD_FOLDER"], record["stored_filename"])


def load_evidence_or_redirect(evidence_id):
    """Return (record, None) or (None, redirect response) if not found."""
    record = get_evidence(evidence_id)
    if record is None:
        flash(f"Evidence record #{evidence_id} was not found.", "error")
        return None, redirect(url_for("main.index"))
    return record, None


def get_file_content_preview(record):
    """Provide a preliminary text preview for plain text files (Review 2 preview)."""
    if record["file_type"] == "Plain text":
        path = evidence_path(record)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(5000)
            except Exception:
                return "Unable to read text preview."
    return None


# ------------------------------------------------------------- auth routes

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(email, password)
        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            session["badge_number"] = user["badge_number"]

            log_activity(
                user_id=user["user_id"],
                user_name=user["name"],
                action="USER_LOGIN",
                details=f"Investigator {user['name']} logged in successfully.",
            )
            flash(f"Welcome back, {user['name']} ({user['role']}).", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid credentials. Use one of the 1-click demo profiles below.", "error")

    all_users = list_users()
    return render_template("login.html", users=all_users)


@bp.route("/logout")
def logout():
    user = get_current_user()
    if user:
        log_activity(
            user_id=user["user_id"],
            user_name=user["name"],
            action="USER_LOGOUT",
            details=f"Investigator {user['name']} signed out.",
        )
    session.clear()
    flash("You have been signed out successfully.", "success")
    return redirect(url_for("main.login"))


@bp.route("/switch-user/<int:user_id>")
def switch_user(user_id):
    """1-click instant demo access for Investigator."""
    user = get_user_by_id(user_id)
    if user:
        session["user_id"] = user["user_id"]
        session["user_name"] = user["name"]
        session["user_role"] = user["role"]
        session["badge_number"] = user["badge_number"]
        log_activity(
            user_id=user["user_id"],
            user_name=user["name"],
            action="USER_LOGIN",
            details=f"Investigator {user['name']} logged in via 1-click access.",
        )
        flash(f"Welcome back, {user['name']} ({user['role']}).", "success")
        return redirect(url_for("main.index"))
    return redirect(url_for("main.login"))


# ------------------------------------------------------------ main routes

@bp.route("/")
@login_required
def index():
    stats = get_dashboard_stats()
    recent_evidence = list_recent_evidence(limit=8)
    cases = list_cases()
    recent_activity = list_recent_activity(limit=10)
    return render_template(
        "index.html",
        stats=stats,
        recent_evidence=recent_evidence,
        cases=cases,
        recent_activity=recent_activity,
    )


# ----------------------------------------------------------- cases routes

@bp.route("/cases")
@login_required
def cases_list():
    status_filter = request.args.get("status", "All")
    all_cases = list_cases(status_filter=status_filter)
    stats = get_dashboard_stats()
    return render_template("cases.html", cases=all_cases, current_filter=status_filter, stats=stats)


@bp.route("/cases/new", methods=["POST"])
@login_required
def new_case():
    user = get_current_user()
    case_number = request.form.get("case_number", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")

    if not case_number or not title:
        flash("Case number and case title are required.", "error")
        return redirect(url_for("main.cases_list"))

    try:
        case_id = create_case(case_number, title, description, priority, user["user_id"])
        flash(f"Investigation Case #{case_number} successfully registered.", "success")
        return redirect(url_for("main.case_detail", case_id=case_id))
    except Exception as e:
        flash(f"Error creating case: {str(e)}", "error")
        return redirect(url_for("main.cases_list"))


@bp.route("/cases/<int:case_id>")
@login_required
def case_detail(case_id):
    case = get_case(case_id)
    if not case:
        flash(f"Case #{case_id} was not found.", "error")
        return redirect(url_for("main.cases_list"))

    case_evidence = list_recent_evidence(limit=50, case_id=case_id)
    case_activity = list_recent_activity(limit=20, case_id=case_id)
    return render_template(
        "case_detail.html",
        case=case,
        evidence_list=case_evidence,
        activity_logs=case_activity,
    )


@bp.route("/cases/<int:case_id>/status", methods=["POST"])
@login_required
def toggle_case_status(case_id):
    """Close an open case or re-open a closed case, logging the audit event."""
    case = get_case(case_id)
    if not case:
        flash(f"Case #{case_id} was not found.", "error")
        return redirect(url_for("main.cases_list"))

    new_status = request.form.get("status")
    reason = request.form.get("reason", "").strip() or None

    if not new_status:
        new_status = "Open" if case["status"] == "Closed" else "Closed"

    user = get_current_user()
    user_id = user["user_id"] if user else 1
    user_name = user["name"] if user else "Investigator"

    update_case_status(case_id, new_status, user_id=user_id, user_name=user_name, reason=reason)

    if new_status == "Closed":
        flash(f"Investigation Case #{case['case_number']} has been CLOSED. Action recorded in audit log.", "success")
    else:
        flash(f"Investigation Case #{case['case_number']} has been RE-OPENED. Action recorded in audit log.", "success")

    return redirect(url_for("main.case_detail", case_id=case_id))


# --------------------------------------------------------- evidence upload

@bp.route("/upload", methods=["POST"])
@login_required
def upload_evidence():
    file = request.files.get("evidence_file")
    case_id_raw = request.form.get("case_id")
    case_id = int(case_id_raw) if case_id_raw and case_id_raw.isdigit() else None
    notes = request.form.get("notes", "").strip() or None

    user = get_current_user()
    user_id = user["user_id"] if user else 1

    # 1. Was a file selected?
    if file is None or file.filename == "":
        flash("No file was selected. Please choose a file to upload.", "error")
        return redirect(request.referrer or url_for("main.index"))

    display_name = clean_display_name(file.filename)
    extension = get_extension(display_name)

    # 2. Is the extension allowed?
    if extension not in current_app.config["ALLOWED_EXTENSIONS"]:
        flash(f"'{display_name}' is not an allowed file type. "
              "Allowed types: PDF, DOC, DOCX, JPG, JPEG, PNG, TXT.", "error")
        return redirect(request.referrer or url_for("main.index"))

    # 3. Is the file empty?
    file_size = get_upload_size(file)
    if file_size == 0:
        flash(f"'{display_name}' is empty (0 bytes) and cannot be recorded as evidence.", "error")
        return redirect(request.referrer or url_for("main.index"))

    # 4. Content signature check
    first_bytes = file.stream.read(1024)
    file.stream.seek(0)
    if not content_matches_extension(first_bytes, extension):
        flash(f"The contents of '{display_name}' do not look like a valid "
              f".{extension} file. The file was not saved.", "error")
        return redirect(request.referrer or url_for("main.index"))

    # 5. Save under safe server-generated name
    stored_filename = f"{uuid.uuid4().hex}.{extension}"
    saved_path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_filename)
    file.save(saved_path)

    # 6. Calculate SHA-256 hash immediately
    sha256_hash = calculate_sha256(saved_path)
    file_type, mime_type = FILE_TYPES[extension]
    uploaded_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    evidence_id = add_evidence(
        original_filename=display_name,
        stored_filename=stored_filename,
        file_type=file_type,
        mime_type=mime_type,
        file_size=file_size,
        sha256_hash=sha256_hash,
        uploaded_at=uploaded_at,
        case_id=case_id,
        uploaded_by=user_id,
        notes=notes,
    )

    current_app.logger.info("Evidence #%s uploaded: %s sha256=%s",
                            evidence_id, stored_filename, sha256_hash)

    flash("File uploaded successfully. SHA-256 hash calculated and recorded.", "success")
    return redirect(url_for("main.evidence_detail", evidence_id=evidence_id))


@bp.route("/evidence/<int:evidence_id>")
@login_required
def evidence_detail(evidence_id):
    record, error_response = load_evidence_or_redirect(evidence_id)
    if error_response:
        return error_response

    text_preview = get_file_content_preview(record)
    evidence_logs = list_recent_activity(limit=10)
    related_logs = [log for log in evidence_logs if log["evidence_id"] == evidence_id]

    return render_template(
        "evidence.html",
        evidence=record,
        text_preview=text_preview,
        audit_logs=related_logs,
    )


@bp.route("/evidence/<int:evidence_id>/preview")
@login_required
def preview_evidence_file(evidence_id):
    """Serve uploaded file securely for image or document preview."""
    record, error_response = load_evidence_or_redirect(evidence_id)
    if error_response:
        return error_response
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        record["stored_filename"],
        as_attachment=False,
    )


@bp.route("/evidence/<int:evidence_id>/delete", methods=["POST"])
@login_required
def delete_evidence_record(evidence_id):
    """Purge evidence metadata from the database and remove stored file if present."""
    record, error_response = load_evidence_or_redirect(evidence_id)
    if error_response:
        return error_response

    # Clean up physical file on disk if it still exists
    filepath = evidence_path(record)
    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

    user = get_current_user()
    user_name = user["name"] if user else "Investigator"
    user_id = user["user_id"] if user else 1

    log_activity(
        user_id=user_id,
        user_name=user_name,
        action="EVIDENCE_PURGED",
        details=f"Evidence #{evidence_id} ('{record['original_filename']}') was purged from register by {user_name}.",
        case_id=record["case_id"],
        evidence_id=evidence_id,
    )

    delete_evidence(evidence_id)
    flash(f"Evidence record #{evidence_id} ('{record['original_filename']}') was successfully removed.", "success")

    if record["case_id"]:
        return redirect(url_for("main.case_detail", case_id=record["case_id"]))
    return redirect(url_for("main.index"))


@bp.route("/evidence/<int:evidence_id>/verify", methods=["POST"])
@login_required
def verify_evidence(evidence_id):
    record, error_response = load_evidence_or_redirect(evidence_id)
    if error_response:
        return error_response

    result = verify_integrity(evidence_path(record), record["sha256_hash"])
    result["checked_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    user = get_current_user()
    user_name = user["name"] if user else "Investigator"
    user_id = user["user_id"] if user else 1

    log_activity(
        user_id=user_id,
        user_name=user_name,
        action="INTEGRITY_VERIFIED",
        details=f"Integrity verification for Evidence #{evidence_id} ({record['original_filename']}): Status {result['status']}",
        case_id=record["case_id"],
        evidence_id=evidence_id,
    )

    current_app.logger.info("Evidence #%s verified: %s", evidence_id, result["status"])

    text_preview = get_file_content_preview(record)
    return render_template(
        "evidence.html",
        evidence=record,
        verification=result,
        text_preview=text_preview,
    )


@bp.route("/evidence/<int:evidence_id>/tamper-test", methods=["POST"])
@login_required
def tamper_test(evidence_id):
    record, error_response = load_evidence_or_redirect(evidence_id)
    if error_response:
        return error_response

    original_path = evidence_path(record)
    if not os.path.isfile(original_path):
        flash("The original evidence file is missing, so the tamper test cannot run.", "error")
        return redirect(url_for("main.evidence_detail", evidence_id=evidence_id))

    stem, extension = record["stored_filename"].rsplit(".", 1)
    copy_filename = f"{stem}_tampered_copy.{extension}"
    copy_path = create_tampered_copy(
        original_path,
        current_app.config["TEST_COPY_FOLDER"],
        copy_filename,
    )

    tamper_result = {
        "copy_filename": copy_filename,
        "tampered_copy": verify_integrity(copy_path, record["sha256_hash"]),
        "original": verify_integrity(original_path, record["sha256_hash"]),
    }

    user = get_current_user()
    user_name = user["name"] if user else "Investigator"
    user_id = user["user_id"] if user else 1

    log_activity(
        user_id=user_id,
        user_name=user_name,
        action="TAMPER_DETECTED" if tamper_result["tampered_copy"]["status"] == "MISMATCH" else "TAMPER_TEST_RUN",
        details=f"Controlled tamper demo on Evidence #{evidence_id}: Modified copy detected as MISMATCH; Original remains MATCH (untouched).",
        case_id=record["case_id"],
        evidence_id=evidence_id,
    )

    current_app.logger.info(
        "Evidence #%s tamper test: copy=%s original=%s",
        evidence_id,
        tamper_result["tampered_copy"]["status"],
        tamper_result["original"]["status"],
    )

    text_preview = get_file_content_preview(record)
    return render_template(
        "evidence.html",
        evidence=record,
        tamper=tamper_result,
        text_preview=text_preview,
    )


# -------------------------------------------------------- audit log route

@bp.route("/activity")
@login_required
def activity_log():
    logs = list_recent_activity(limit=100)
    return render_template("activity.html", logs=logs)
