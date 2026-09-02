/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { InvoiceButton } from "@point_of_sale/app/screens/ticket_screen/invoice_button/invoice_button";

patch(InvoiceButton.prototype, {
    async _invoiceOrder() {
        // Delegate to the standard v18 invoice flow
        // (custom CPE fields are set server-side via _prepare_invoice_vals)
        await super._invoiceOrder(...arguments);
    },
});
