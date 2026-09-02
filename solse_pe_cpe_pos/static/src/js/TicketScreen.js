/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {
    async _onDoRefund() {
        const order = this.getSelectedSyncedOrder();
        if (!order) return;

        const docTypeSaleId = order.get_doc_type_sale();
        const docVenta = this.pos.doc_type_sale_by_id?.[docTypeSaleId];
        const notaCredito = docVenta?.nota_credito;

        if (!notaCredito) {
            this.dialog.add(AlertDialog, {
                title: _t('Aviso'),
                body: _t('Establezca un tipo de comprobante para la nota de crédito'),
            });
            return;
        }

        // Run the standard refund flow
        await super._onDoRefund(...arguments);

        // After refund order is created, set the credit note document type
        const destinationOrder = this.pos.get_order();
        if (destinationOrder) {
            const ncId = Array.isArray(notaCredito) ? notaCredito[0] : notaCredito;
            destinationOrder.set_doc_type_sale(ncId);
        }
    },
});
