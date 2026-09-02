/** @odoo-module **/
// In Odoo 18, partner editing in POS uses a backend form view.
// The custom partner fields (doc_number, l10n_latam_identification_type_id, etc.)
// are shown directly in that form via the existing res.partner view.
// The RUC/DNI lookup is provided by solse_vat_pos_pe (which this module depends on).
// No additional ClientDetailsEdit patch needed here.
