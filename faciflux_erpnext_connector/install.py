from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def _technical_field(label):
    return {
        "label": label,
        "fieldtype": "Data",
        "read_only": 1,
        "allow_on_submit": 1,
        "no_copy": 1,
        "hidden": 1,
    }


def apply_custom_fields():
    # These are integration identities, never an operational source of truth.
    # Do not set global uniqueness: one FluxOS operation may legitimately create
    # a Material Transfer and a Manufacture Stock Entry.
    create_custom_fields({
        "Stock Entry": [{"fieldname": "fluxos_operation_key", **_technical_field("FluxOS Operation Key")}],
        "Sales Order": [{"fieldname": "fluxos_operation_key", **_technical_field("FluxOS Operation Key")}],
        "Delivery Note": [{"fieldname": "fluxos_operation_key", **_technical_field("FluxOS Operation Key")}],
        "Work Order": [{"fieldname": "fluxos_operation_key", **_technical_field("FluxOS Operation Key")}],
        "Customer": [{"fieldname": "fluxos_customer_external_id", **_technical_field("FluxOS Customer External ID")}],
        "Item": [{"fieldname": "fluxos_product_external_id", **_technical_field("FluxOS Product External ID")}],
        "BOM": [{"fieldname": "fluxos_bom_external_id", **_technical_field("FluxOS BOM External ID")}],
    }, update=True)
