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
        "Stock Entry": {"fluxos_operation_key": _technical_field("FluxOS Operation Key")},
        "Sales Order": {"fluxos_operation_key": _technical_field("FluxOS Operation Key")},
        "Delivery Note": {"fluxos_operation_key": _technical_field("FluxOS Operation Key")},
        "Work Order": {"fluxos_operation_key": _technical_field("FluxOS Operation Key")},
        "Customer": {"fluxos_customer_external_id": _technical_field("FluxOS Customer External ID")},
        "Item": {"fluxos_product_external_id": _technical_field("FluxOS Product External ID")},
        "BOM": {"fluxos_bom_external_id": _technical_field("FluxOS BOM External ID")},
    }, update=True)
