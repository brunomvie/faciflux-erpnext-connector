import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import frappe
import requests


def _config():
    enabled = os.getenv("FACIFLUX_CONNECTOR_ENABLED", "").lower() == "true"
    receiver_url = os.getenv("FACIFLUX_CONNECTOR_RECEIVER_URL", "").strip()
    secret = os.getenv("FACIFLUX_CONNECTOR_HMAC_SECRET", "")
    key_id = os.getenv("FACIFLUX_CONNECTOR_KEY_ID", "erpnext-v1").strip()
    if enabled:
        parsed = urlparse(receiver_url)
        insecure_allowed = os.getenv("FACIFLUX_CONNECTOR_ALLOW_INSECURE_HTTP", "").lower() == "true"
        if not receiver_url or (parsed.scheme != "https" and not (insecure_allowed and parsed.scheme == "http")):
            raise frappe.ValidationError("FACIFLUX_CONNECTOR_RECEIVER_URL deve usar HTTPS")
        if len(secret) < 32 or not key_id:
            raise frappe.ValidationError("Segredo ou key id do conector Faciflux inválido")
    return {
        "enabled": enabled,
        "receiver_url": receiver_url,
        "secret": secret,
        "key_id": key_id,
        "timeout": max(1, int(os.getenv("FACIFLUX_CONNECTOR_TIMEOUT_SECONDS", "10"))),
        "batch_size": min(100, max(1, int(os.getenv("FACIFLUX_CONNECTOR_BATCH_SIZE", "20")))),
        "max_attempts": min(100, max(1, int(os.getenv("FACIFLUX_CONNECTOR_MAX_ATTEMPTS", "12")))),
    }


def _utcnow():
    return datetime.now(timezone.utc)


def _claim_events(batch_size):
    # SKIP LOCKED permits more than one worker without sending an event twice at
    # the same time. The event_id remains the end-to-end idempotency key.
    names = frappe.db.sql(
        """
        SELECT name FROM `tabFaciflux Outbox Event`
        WHERE status IN ('Pending', 'Retry')
          AND (next_attempt_at IS NULL OR next_attempt_at <= UTC_TIMESTAMP())
        ORDER BY creation ASC
        LIMIT %s
        FOR UPDATE SKIP LOCKED
        """,
        (batch_size,),
        pluck="name",
    )
    events = []
    for name in names:
        frappe.db.sql(
            """
            UPDATE `tabFaciflux Outbox Event`
               SET status = 'Delivering',
                   attempts = COALESCE(attempts, 0) + 1,
                   last_attempt_at = %s
             WHERE name = %s
            """,
            (_utcnow(), name),
        )
        events.append(frappe.get_doc("Faciflux Outbox Event", name))
    frappe.db.commit()
    return events


def _retry_at(attempts):
    seconds = min(900, 30 * (2 ** max(0, int(attempts) - 1)))
    return _utcnow() + timedelta(seconds=seconds)


def _deliver(event, config):
    body = event.payload_json.encode("utf-8")
    timestamp = _utcnow().isoformat()
    signature = hmac.new(
        config["secret"].encode("utf-8"),
        timestamp.encode("utf-8") + b"." + body,
        hashlib.sha256,
    ).hexdigest()
    response = requests.post(
        config["receiver_url"],
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Faciflux-Key-Id": config["key_id"],
            "X-Faciflux-Event-Id": event.event_id,
            "X-Faciflux-Event-Timestamp": timestamp,
            "X-Faciflux-Signature": f"sha256={signature}",
        },
        timeout=config["timeout"],
    )
    if not 200 <= response.status_code < 300:
        raise RuntimeError(f"FluxOS respondeu HTTP {response.status_code}")


def _mark_delivered(event):
    frappe.db.set_value("Faciflux Outbox Event", event.name, {
        "status": "Delivered",
        "delivered_at": _utcnow(),
        "last_error": None,
    }, update_modified=False)
    frappe.db.commit()


def _mark_failed(event, error, config):
    attempts = int(event.attempts or 0)
    values = {
        "status": "Dead Letter" if attempts >= config["max_attempts"] else "Retry",
        "last_error": str(error)[:1400],
    }
    if values["status"] == "Retry":
        values["next_attempt_at"] = _retry_at(attempts)
    frappe.db.set_value("Faciflux Outbox Event", event.name, values, update_modified=False)
    frappe.db.commit()


def deliver_pending_events():
    config = _config()
    if not config["enabled"]:
        return
    for event in _claim_events(config["batch_size"]):
        try:
            _deliver(event, config)
            _mark_delivered(event)
        except Exception as error:
            _mark_failed(event, error, config)
            frappe.log_error(title="Faciflux outbox delivery failed", message=frappe.get_traceback())
