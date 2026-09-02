/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";

let ejecutando = false;

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
    },

    onDocTypeSelect(ev) {
        const id = parseInt(ev.currentTarget.dataset.docId) || 0;
        this.currentOrder.set_doc_type_sale(id);
    },

    async validate_journal_invoice() {
        const order = this.pos.get_order();
        const client = order.get_partner();
        let res = false;

        if (!client) {
            if (order.es_cpe() && this.pos.config.cliente_varios) {
                const varios = this.pos.models["res.partner"].get(this.pos.config.cliente_varios[0]);
                if (varios) order.set_partner(varios);
            }
        }

        if (!order.get_partner()) {
            this.dialog.add(AlertDialog, {
                title: _t('Error en cliente'),
                body: _t('El cliente es necesario'),
            });
            return true;
        }

        const doc_type = order.get_doc_type();
        const doc_number = order.get_doc_number();
        const val_diario = order.check_pe_journal();
        if (!val_diario[0]) {
            this.dialog.add(AlertDialog, {
                title: _t('Error en el diario'),
                body: _t(val_diario[1]),
            });
            return true;
        }

        const is_validate = this.pos.validate_pe_doc(doc_type, doc_number);
        const cpe_type = order.get_cpe_type();

        if (this.pos.company.sunat_amount < order.get_total_with_tax() && !doc_type && !doc_number) {
            await ask(this.dialog, {
                title: _t('Seleccione un cliente'),
                body: _t('Debe seleccionar un cliente con RUC ó DNI válido antes de poder facturar su pedido.'),
            });
            return true;
        }

        if (['1', '6'].includes(doc_type) && !is_validate) {
            await ask(this.dialog, {
                title: _t('Seleccione el Cliente'),
                body: _t('Debe seleccionar un cliente con RUC ó DNI válido antes de poder facturar su pedido.'),
            });
            return true;
        }

        if (cpe_type === '01' && doc_type !== '6') {
            await ask(this.dialog, {
                title: _t('Seleccione el Cliente'),
                body: _t('Debe seleccionar un cliente con RUC antes de poder facturar su pedido.'),
            });
            return true;
        }

        if (cpe_type === '03' && doc_type === '6') {
            await ask(this.dialog, {
                title: _t('Seleccione el Cliente'),
                body: _t('Debe seleccionar un cliente con DNI antes de poder facturar su pedido.'),
            });
            return true;
        }

        if (cpe_type === '03' && doc_type !== '1' && this.pos.company.sunat_amount < order.get_total_with_tax()) {
            this.dialog.add(AlertDialog, {
                title: _t('Aviso'),
                body: _t('Para montos iguales o mayores a %s son obligatorios el Tipo de Doc. y Número', this.pos.company.sunat_amount),
            });
            return true;
        }

        order.pe_invoice_date = luxon.DateTime.now().toFormat('yyyy-MM-dd HH:mm:ss');
        return res;
    },

    async _isOrderValid(isForceValidate) {
        const order = this.pos.get_order();
        const tipo_doc_venta = order.get_cpe_type();
        const monto_orden = order.get_total_with_tax();

        // Validate line amounts
        for (const line of order.get_orderlines()) {
            if (line.get_unit_price() === 0) {
                this.dialog.add(AlertDialog, {
                    title: _t('Aviso'),
                    body: _t('El monto de las líneas no puede ser 0 para un comprobante electrónico'),
                });
                ejecutando = false;
                return false;
            }
            if (line.get_quantity() === 0) {
                this.dialog.add(AlertDialog, {
                    title: _t('Aviso'),
                    body: _t('La cantidad no puede ser 0 para un comprobante electrónico'),
                });
                ejecutando = false;
                return false;
            }
        }

        if (!tipo_doc_venta) {
            if (this.pos.config.doc_venta_defecto) {
                order.set_doc_type_sale(this.pos.config.doc_venta_defecto[0] || this.pos.config.doc_venta_defecto);
            } else {
                this.dialog.add(AlertDialog, {
                    title: _t('Aviso'),
                    body: _t('Defina un tipo de documento para el comprobante'),
                });
                ejecutando = false;
                return false;
            }
        }

        if (!order.get_partner() && order.es_cpe() && this.pos.config.cliente_varios) {
            const varios = this.pos.models["res.partner"].get(this.pos.config.cliente_varios[0]);
            if (varios) order.set_partner(varios);
        }

        const res = await super._isOrderValid(isForceValidate);
        if (!res) return res;

        if (this.pos.config.module_account && order.es_cpe()) {
            if (await this.validate_journal_invoice()) {
                return false;
            }
        }
        return res;
    },

    async validateOrder(isForceValidate) {
        if (ejecutando) return;
        ejecutando = true;
        try {
            await super.validateOrder(isForceValidate);
        } finally {
            ejecutando = false;
        }
    },
});
