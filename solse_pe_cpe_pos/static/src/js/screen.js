/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { numeroALetras } from "@solse_pe_cpe_pos/lib/NumeroALetras";
import { qrCodeSrc } from "@point_of_sale/utils";

const PARTNER_STATES = [
    { code: 'ACTIVO', name: 'ACTIVO' },
    { code: 'BAJA DE OFICIO', name: 'BAJA DE OFICIO' },
    { code: 'BAJA PROVISIONAL', name: 'BAJA PROVISIONAL' },
    { code: 'SUSPENSION TEMPORAL', name: 'SUSPENSION TEMPORAL' },
    { code: 'INHABILITADO-VENT.UN', name: 'INHABILITADO-VENT.UN' },
    { code: 'BAJA MULT.INSCR. Y O', name: 'BAJA MULT.INSCR. Y O' },
    { code: 'PENDIENTE DE INI. DE', name: 'PENDIENTE DE INI. DE' },
    { code: 'OTROS OBLIGADOS', name: 'OTROS OBLIGADOS' },
    { code: 'NUM. INTERNO IDENTIF', name: 'NUM. INTERNO IDENTIF' },
    { code: 'ANULACION - ACTO ILI', name: 'ANULACION - ACTO ILI' },
    { code: 'BAJA PROV. POR OFICI', name: 'BAJA PROV. POR OFICI' },
    { code: 'ANULACION - ERROR SU', name: 'ANULACION - ERROR SU' },
];

const PARTNER_CONDITIONS = [
    { code: 'HABIDO', name: 'HABIDO' },
    { code: 'NO HALLADO', name: 'NO HALLADO' },
    { code: 'NO HABIDO', name: 'NO HABIDO' },
    { code: 'PENDIENTE', name: 'PENDIENTE' },
    { code: 'NO HALLADO SE MUDO D', name: 'NO HALLADO SE MUDO D' },
    { code: 'NO HALLADO NO EXISTE', name: 'NO HALLADO NO EXISTE' },
    { code: 'NO HALLADO FALLECIO', name: 'NO HALLADO FALLECIO' },
    { code: 'NO HALLADO OTROS MOT', name: 'NO HALLADO OTROS MOT' },
    { code: 'NO APLICABLE', name: 'NO APLICABLE' },
    { code: 'NO HALLADO NRO.PUERT', name: 'NO HALLADO NRO.PUERT' },
    { code: 'NO HALLADO CERRADO', name: 'NO HALLADO CERRADO' },
    { code: 'POR VERIFICAR', name: 'POR VERIFICAR' },
];

patch(PosStore.prototype, {
    async processServerData() {
        await super.processServerData(...arguments);

        this.partner_states = PARTNER_STATES;
        this.partner_conditions = PARTNER_CONDITIONS;

        // Build doc type lookup maps (also done by solse_vat_pos_pe if installed)
        this.doc_code_by_id = this.doc_code_by_id || {};
        this.doc_types = this.doc_types || [];
        const idTypeModel = this.models["l10n_latam.identification.type"];
        if (idTypeModel && !this.doc_types.length) {
            const docs = idTypeModel.getAll();
            this.doc_types = docs;
            for (const doc of docs) {
                this.doc_code_by_id[doc.id] = doc.l10n_pe_vat_code;
            }
        }

        // Document types for sale — used in templates via pos.l10n_latam_document_type_ids
        this.l10n_latam_document_type_ids = [];
        const docTypeModel = this.models["l10n_latam.document.type"];
        if (docTypeModel) {
            this.l10n_latam_document_type_ids = docTypeModel.getAll();
        }

        // Payment terms — used in templates via pos.invoice_payment_term_ids
        this.invoice_payment_term_ids = [];
        const termModel = this.models["account.payment.term"];
        if (termModel) {
            this.invoice_payment_term_ids = termModel.getAll();
        }

        // Location cascades
        this.departamentos = [];
        this.departamentos_pais = {};
        const stateModel = this.models["res.country.state"];
        if (stateModel) {
            const states = stateModel.getAll();
            this.departamentos = states;
            for (const s of states) {
                const cId = Array.isArray(s.country_id) ? s.country_id[0] : s.country_id?.id;
                if (cId) {
                    (this.departamentos_pais[cId] = this.departamentos_pais[cId] || []).push(s);
                }
            }
        }

        this.provincias = [];
        this.provincias_departamento = {};
        const cityModel = this.models["res.city"];
        if (cityModel) {
            const cities = cityModel.getAll();
            this.provincias = cities;
            for (const c of cities) {
                const sId = Array.isArray(c.state_id) ? c.state_id[0] : c.state_id?.id;
                if (sId) {
                    (this.provincias_departamento[sId] = this.provincias_departamento[sId] || []).push(c);
                }
            }
        }

        this.distritos = [];
        this.distritos_provincia = {};
        const distModel = this.models["l10n_pe.res.city.district"];
        if (distModel) {
            const dists = distModel.getAll();
            this.distritos = dists;
            for (const d of dists) {
                const cId = Array.isArray(d.city_id) ? d.city_id[0] : d.city_id?.id;
                if (cId) {
                    (this.distritos_provincia[cId] = this.distritos_provincia[cId] || []).push(d);
                }
            }
        }
    },

    validate_pe_doc(doc_type, doc_number) {
        if (!doc_type || !doc_number) return false;
        if (doc_number.length === 8 && doc_type === '1') return true;
        if (doc_number.length === 11 && doc_type === '6') {
            const factor = '5432765432';
            let sum = 0;
            try { parseInt(doc_number); } catch { return false; }
            for (let i = 0; i < factor.length; i++) {
                sum += parseInt(factor[i]) * parseInt(doc_number[i]);
            }
            const sub = 11 - (sum % 11);
            const dig = sub === 10 ? 0 : sub === 11 ? 1 : sub;
            return parseInt(doc_number[10]) === dig;
        }
        if (doc_number.length >= 3 && ['0', '4', '7', 'A'].includes(doc_type)) return true;
        if (doc_type.length >= 2) return true;
        return false;
    },
});

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(vals);
        // Many2one fields (l10n_latam_document_type_id, invoice_payment_term_id) are handled
        // by the v18 model system — super.setup() already sets them as record objects.
        // Only set plain (non-relational) extra fields here.
        this.number = vals.number || false;
        this.number_ref = vals.number_ref || false;
        this.date_invoice = vals.date_invoice || false;
        this.pe_invoice_date = vals.pe_invoice_date || false;
    },

    check_pe_journal() {
        const client = this.get_partner();
        const doc_type = client ? client.doc_type : false;
        const journal_type = this.get_cpe_type();
        if (!journal_type) return [false, 'Seleccione un diario valido'];
        if (journal_type === '01' && doc_type !== '6') {
            return [false, 'El tipo de documento del cliente no es valido para facturas'];
        }
        if (journal_type === '03' && doc_type === '6') {
            return [false, 'El tipo de documento del cliente no es valido para boletas'];
        }
        return [true, 'OK'];
    },

    get_cpe_type() {
        // l10n_latam_document_type_id is a record object in v18 model system
        const doc = this.l10n_latam_document_type_id;
        if (!doc) return false;
        return doc.code || false;
    },

    es_cpe() {
        return !!this.get_cpe_type();
    },

    es_un_cpe() {
        const doc = this.l10n_latam_document_type_id;
        return doc ? !!doc.is_cpe : false;
    },

    get_cpe_qr() {
        const company = this.models["res.company"]?.getFirst();
        const parts = [
            company?.vat || '',
            this.get_cpe_type() || ' ',
            this.get_number() || ' ',
            this.get_total_tax() || 0,
            this.get_total_with_tax() || 0,
            luxon.DateTime.now().toFormat('yyyy-MM-dd'),
            this.get_doc_type() || '-',
            this.get_doc_number() || '-',
        ];
        return parts.join('|');
    },

    set_doc_type_sale(id) {
        // In v18 model system, many2one fields must be set to record objects, not integers.
        // The serializer does record[name]?.id — an integer has no .id, so it serializes as undefined.
        const doc = id ? this.models["l10n_latam.document.type"]?.get(id) : null;
        this.l10n_latam_document_type_id = doc || null;
    },

    get_doc_type_sale() {
        // Return the record object's ID (integer), or 0 if not set.
        const val = this.l10n_latam_document_type_id;
        return val?.id || 0;
    },

    set_invoice_payment_term(id) {
        const term = id ? this.models["account.payment.term"]?.get(id) : null;
        this.invoice_payment_term_id = term || null;
    },

    get_invoice_payment_term() {
        const val = this.invoice_payment_term_id;
        return val?.id || 0;
    },

    get_payment_term() {
        const term = this.invoice_payment_term_id;
        return term ? term.name : false;
    },

    get_number() {
        return this.number || '';
    },

    get_number_ref() {
        return this.number_ref || '';
    },

    get_doc_type() {
        const client = this.get_partner();
        if (!client) return false;
        if (client.parent_id) return client.cod_doc_rel;
        return client.doc_type || false;
    },

    get_doc_number() {
        const client = this.get_partner();
        if (!client) return '';
        if (client.parent_id) return client.numero_temp || '';
        return client.doc_number || '';
    },

    get_amount_text() {
        const monto = Math.abs(this.get_total_with_tax());
        const currency = this.config?.currency_id;
        return numeroALetras(monto, {
            plural: currency?.plural_name,
            singular: currency?.singular_name,
            centPlural: currency?.show_fraction ? currency.fraction_name : '',
            centSingular: currency?.show_fraction ? currency.fraction_name : '',
        });
    },

    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        const client = this.get_partner();
        const company = this.models["res.company"]?.getFirst();
        const cpe_type = this.get_cpe_type() || false;
        const cpe_number = this.get_number() || '';
        const qr_text = cpe_type && cpe_type !== '00' ? this.get_cpe_qr() : false;
        // For CPE receipts:
        // - Replace `name` (POS "Order 00001") with the CPE document number in the footer.
        // - Suppress `trackingNumber` in headerData so it doesn't appear at the top of the receipt
        //   (the CPE number in our custom block already identifies the document).
        const pos_reference = result.name;
        const name = (cpe_type && cpe_number) ? cpe_number : pos_reference;
        const printHeaderData = cpe_type
            ? { ...result.headerData, trackingNumber: false }
            : result.headerData;
        const doc_number = this.get_doc_number() || '';
        const doc_type_code = this.get_doc_type() || '';
        const DOC_LABELS = { '1': 'DNI', '6': 'RUC', '4': 'C.E.', '7': 'Pasaporte', 'A': 'Cédula Dipl.', '0': '-' };
        const doc_type_label = DOC_LABELS[doc_type_code] || doc_type_code;

        // Build a clean single-line address from available partner fields
        const _addrPart = (rec) => (rec && typeof rec === 'object' ? rec.name : null);
        const addrParts = client ? [
            client.street || '',
            _addrPart(client.l10n_pe_district),
            _addrPart(client.city_id),
            _addrPart(client.state_id),
        ].filter(Boolean) : [];

        return {
            ...result,
            name,
            pos_reference,
            headerData: printHeaderData,
            cpe_type,
            cpe_number,
            doc_number,
            doc_type_label,
            number_ref: this.number_ref || false,
            amount_text: this.get_amount_text(),
            invoice_payment_term: this.get_invoice_payment_term(),
            payment_term_name: this.get_payment_term() || '',
            sunat_qr_code: qr_text ? qrCodeSrc(qr_text, { size: 150 }) : false,
            company_website: company?.website || '',
            company: company ? {
                name: company.name || '',
                phone: company.phone || '',
                street: company.street || '',
                city: company.city_id?.name || '',
                state: company.state_id?.name || '',
                website: company.website || '',
            } : false,
            client: client ? {
                name: client.name,
                phone: client.phone || '',
                email: client.email || '',
                doc_number,
                doc_type_label,
                address: addrParts.join(', '),
            } : false,
        };
    },
});
