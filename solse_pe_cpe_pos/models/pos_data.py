# -*- coding: utf-8 -*-
from odoo import api, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _load_pos_data_models(self, config_id):
        models_list = super()._load_pos_data_models(config_id)
        extra = [
            'account.payment.term',
            'l10n_latam.document.type',
            'res.city',
            'l10n_pe.res.city.district',
        ]
        for m in extra:
            if m not in models_list:
                models_list.append(m)
        return models_list


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        if not fields:
            return fields
        extra = [
            'number', 'number_ref', 'l10n_latam_document_type_id',
            'invoice_sequence_number', 'date_invoice', 'pe_invoice_date',
            'invoice_payment_term_id', 'refunded_order_id',
        ]
        return fields + [f for f in extra if f not in fields]


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    @api.model
    def _load_pos_data_domain(self, data):
        return []

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'note']

    @api.model
    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        return {'data': self.search_read(domain, fields, load=False), 'fields': fields}


class L10nLatamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    @api.model
    def _load_pos_data_domain(self, data):
        config_data = data['pos.config']['data'][0]
        doc_ids = config_data.get('documento_venta_ids', [])
        return [('id', 'in', doc_ids)]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'code', 'internal_type', 'active']

    @api.model
    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        return {'data': self.search_read(domain, fields, load=False), 'fields': fields}


class ResCity(models.Model):
    _inherit = 'res.city'

    @api.model
    def _load_pos_data_domain(self, data):
        return []

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'country_id', 'state_id', 'l10n_pe_code', 'zipcode']

    @api.model
    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        return {'data': self.search_read(domain, fields, load=False), 'fields': fields}


class L10nPeResCityDistrict(models.Model):
    _inherit = 'l10n_pe.res.city.district'

    @api.model
    def _load_pos_data_domain(self, data):
        return []

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'city_id', 'code']

    @api.model
    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        return {'data': self.search_read(domain, fields, load=False), 'fields': fields}


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        extra = ['singular_name', 'plural_name', 'fraction_name', 'show_fraction']
        return fields + [f for f in extra if f not in fields and f in self._fields]


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        extra = ['street', 'street_name', 'sunat_amount']
        return fields + [f for f in extra if f not in fields and f in self._fields]


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        # [] means "all fields" in Odoo ORM — do not restrict
        if not fields:
            return fields
        extra = ['documento_venta_ids']
        return fields + [f for f in extra if f not in fields]
