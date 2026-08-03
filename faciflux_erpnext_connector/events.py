import hashlib
import json
import uuid
from datetime import datetime, timezone

import frappe


def _event_type(doc, action):
    return f"erpnext.{frappe.scrub(doc.doctype)}.{action}.v1"


def _document_payload(doc):
    # Deliberately restrict the envelope to auditable operational data. Large child
    # tables may be projected by a specific consumer when that use case is enabled.
    fields = ("name", "doctype", "docstatus", "modified", "modified_by", "owner", "status")
    return {field: doc.get(field) for field in fields if doc.get(field) is not None}


def _record_event(doc, action):
    event_id = str(uuid.uuid4())
    payload = _document_payload(doc)
    event = {
        "event_id": event_id,
        "event_type": _event_type(doc, action),
        "schema_version": "1",
        "producer": "erpnext",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "aggregate": {
            "type": doc.doctype,
            "id": doc.name,
            "version": str(doc.modified or ""),
        },
        "correlation_id": doc.get("fluxos_operation_key"),
        "payload": payload,
    }
    payload_json = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    frappe.get_doc({
        "doctype": "Faciflux Outbox Event",
        "event_id": event_id,
        "event_type": event["event_type"],
        "schema_version": event["schema_version"],
        "aggregate_type": doc.doctype,
        "aggregate_id": doc.name,
        "aggregate_version": event["aggregate"]["version"],
        "correlation_id": event["correlation_id"],
        "occurred_at": event["occurred_at"],
        "payload_json": payload_json,
        "payload_checksum": hashlib.sha256(payload_json.encode("utf-8")).hexdigest(),
        "status": "Pending",
    }).insert(ignore_permissions=True)


def record_submitted_event(doc, method=None):
    _record_event(doc, "submitted")


def record_cancelled_event(doc, method=None):
    _record_event(doc, "cancelled")


def record_changed_event(doc, method=None):
    _record_event(doc, "changed")


def record_master_data_event(doc, method=None):
    _record_event(doc, "changed")
