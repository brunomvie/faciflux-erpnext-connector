app_name = "faciflux_erpnext_connector"
app_title = "Faciflux ERPNext Connector"
app_publisher = "Faciflux"
app_description = "Transactional ERPNext to FluxOS connector"
app_email = "tecnologia@faciflux.com.br"
app_license = "MIT"

after_install = "faciflux_erpnext_connector.install.apply_custom_fields"
after_migrate = "faciflux_erpnext_connector.install.apply_custom_fields"

doc_events = {
    "Sales Order": {
        "on_submit": "faciflux_erpnext_connector.events.record_submitted_event",
        "on_cancel": "faciflux_erpnext_connector.events.record_cancelled_event",
        "on_update_after_submit": "faciflux_erpnext_connector.events.record_changed_event",
    },
    "Delivery Note": {
        "on_submit": "faciflux_erpnext_connector.events.record_submitted_event",
        "on_cancel": "faciflux_erpnext_connector.events.record_cancelled_event",
        "on_update_after_submit": "faciflux_erpnext_connector.events.record_changed_event",
    },
    "Stock Entry": {
        "on_submit": "faciflux_erpnext_connector.events.record_submitted_event",
        "on_cancel": "faciflux_erpnext_connector.events.record_cancelled_event",
        "on_update_after_submit": "faciflux_erpnext_connector.events.record_changed_event",
    },
    "Work Order": {
        "on_submit": "faciflux_erpnext_connector.events.record_submitted_event",
        "on_cancel": "faciflux_erpnext_connector.events.record_cancelled_event",
        "on_update_after_submit": "faciflux_erpnext_connector.events.record_changed_event",
    },
    "Customer": {
        "after_insert": "faciflux_erpnext_connector.events.record_master_data_event",
        "on_update": "faciflux_erpnext_connector.events.record_master_data_event",
    },
    "Item": {
        "after_insert": "faciflux_erpnext_connector.events.record_master_data_event",
        "on_update": "faciflux_erpnext_connector.events.record_master_data_event",
    },
    "BOM": {
        "on_submit": "faciflux_erpnext_connector.events.record_submitted_event",
        "on_cancel": "faciflux_erpnext_connector.events.record_cancelled_event",
        "on_update_after_submit": "faciflux_erpnext_connector.events.record_changed_event",
    },
}

scheduler_events = {
    "all": [
        "faciflux_erpnext_connector.outbox.deliver_pending_events",
    ],
}
