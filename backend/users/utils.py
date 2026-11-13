"""Shared helpers for the users app."""
import hashlib
import ipaddress

from django.conf import settings


def normalize_backup_code(code):
    """Normalize a 2FA backup code: strip separators/whitespace and upper-case."""
    return (code or '').strip().replace('-', '').replace(' ', '').upper()


def hash_backup_code(code):
    """Hash a backup code for storage/comparison (separator and case insensitive)."""
    return hashlib.sha256(normalize_backup_code(code).encode()).hexdigest()


def _legacy_hash_candidates(code):
    """
    Hashes used by older versions, which hashed the code exactly as displayed
    (upper-case, dash separated groups of four). Kept so codes issued before the
    normalization fix continue to work.
    """
    normalized = normalize_backup_code(code)
    dashed = '-'.join(normalized[i:i + 4] for i in range(0, len(normalized), 4))
    return {hashlib.sha256(dashed.encode()).hexdigest()}


def consume_backup_code(user, code):
    """
    Check a backup code against the user's stored hashes and remove it if valid.
    The caller is responsible for saving the user. Returns True if the code matched.
    """
    if not normalize_backup_code(code):
        return False
    candidates = {hash_backup_code(code)} | _legacy_hash_candidates(code)
    stored = list(user.twofa_backup_codes or [])
    for candidate in candidates:
        if candidate in stored:
            stored.remove(candidate)
            user.twofa_backup_codes = stored
            return True
    return False


def get_client_ip(request):
    """
    Best-effort client IP.

    X-Forwarded-For is client-controlled, so it is only honoured when the request
    reached Django from a trusted proxy (loopback/private address, e.g. nginx on the
    same host). In that case the right-most entry is the address the proxy itself
    saw; entries to the left of it can be forged by the client.
    """
    remote_addr = request.META.get('REMOTE_ADDR') or ''
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded and getattr(settings, 'TRUST_PROXY_HEADERS', True):
        try:
            via_proxy = (not remote_addr) or ipaddress.ip_address(remote_addr).is_private
        except ValueError:
            via_proxy = False
        if via_proxy:
            candidate = forwarded.split(',')[-1].strip()
            try:
                ipaddress.ip_address(candidate)
                return candidate
            except ValueError:
                pass
    return remote_addr or None
