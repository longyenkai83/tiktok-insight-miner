"""Atomic local JSON ledger, OS file locks and optimistic stale-view protection."""
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .governance_engine import apply_reviews, checked_queue, prepare_review, record_review
from .governance_models import ReviewQueue, VerifiedInsightsEnvelope
from .pattern_models import artifact_hash


@contextmanager
def file_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Stable lock inode: do not unlink it while other processes may have it open.
    with path.with_suffix(path.suffix + ".lock").open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError("review store busy; reload and retry") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".review-", suffix=".tmp", delete=False) as stream:
            temp = Path(stream.name)
            stream.write(value.model_dump_json(indent=2))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def load_reviews(path):
    return ReviewQueue.model_validate_json(Path(path).read_text(encoding="utf-8"))


def load_verified(path):
    return VerifiedInsightsEnvelope.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _save_append_only(path, new, old):
    new = checked_queue(new)
    if old is not None:
        if new.events[:len(old.events)] != old.events or new.snapshots[:len(old.snapshots)] != old.snapshots:
            raise ValueError("review history/snapshots are append-only")
    atomic_json(path, new)


def prepare_review_file(insights, path):
    path = Path(path)
    with file_lock(path):
        old = load_reviews(path) if path.exists() else None
        new = prepare_review(insights, old)
        if new != old:
            _save_append_only(path, new, old)
        return new


def record_review_file(path, action, *, expected_history_hash):
    path = Path(path)
    with file_lock(path):
        old = load_reviews(path)
        # Exact retry succeeds even after the caller lost the original response.
        prior = next((e for e in old.events if e.action.request_id == action.request_id), None)
        if prior:
            return record_review(old, action)
        if artifact_hash(old) != expected_history_hash:
            raise ValueError("review history changed; reload before deciding")
        new = record_review(old, action)
        _save_append_only(path, new, old)
        return new


def apply_review_file(reviews_path, output_path):
    reviews_path, output_path = Path(reviews_path), Path(output_path)
    if reviews_path.resolve() == output_path.resolve():
        raise ValueError("verified output must not overwrite review history")
    with file_lock(reviews_path):
        result = apply_reviews(load_reviews(reviews_path))
        # Serialize writers of the projection as well as the authoritative ledger.
        with file_lock(output_path):
            if output_path.exists():
                load_verified(output_path)  # Never overwrite source/ledger/unrelated files.
            atomic_json(output_path, result)
        return result
