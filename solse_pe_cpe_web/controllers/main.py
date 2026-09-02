# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale as Base
from odoo.osv import expression
import logging
_logger = logging.getLogger(__name__)

# Campos permitidos para escritura desde el checkout web
_PARTNER_WRITABLE_FIELDS = {
    'name', 'email', 'phone', 'mobile',
    'street', 'street2', 'city', 'zip',
    'country_id', 'state_id', 'city_id', 'l10n_pe_district',
    'l10n_latam_identification_type_id', 'doc_number', 'vat',
    'company_type', 'pe_invoice_code',
}


class WebsiteSale(Base):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        search_domain = super()._get_search_domain(search, category, attrib_values, search_in_description)
        search_domain = expression.AND([search_domain, [('is_published', '=', True)]])
        return search_domain

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            # v18: geoip accesible via request.geoip
            geoip = getattr(request, 'geoip', None) or {}
            country_code = geoip.get('country_code') if geoip else None
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return request.redirect('/shop/checkout')
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:
                return request.redirect('/shop/checkout')

        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.pasar_variables_web(post)
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    ruta = kw.get('callback') or '/shop/confirm_order'
                    return request.redirect(ruta)

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        country = (country or request.website.company_id.country_id)

        tipos_docs = request.env['l10n_latam.identification.type'].search([('country_id', '=', request.website.company_id.country_id.id)])
        tipos_comprobantes = [
            {'id': '01', 'name': 'Factura'},
            {'id': '03', 'name': 'Boleta'},
            {'id': '11', 'name': 'Otro documento'},
        ]

        provincias = False
        if 'state_id' in values:
            state_val = values['state_id']
            state_id = state_val if isinstance(state_val, (str, int)) else state_val.id
            state_rec = request.env['res.country.state'].search([('id', '=', state_id)], limit=1)
            provincias = state_rec.get_website_sale_privincias() if state_rec else False

        distritos = False
        if 'city_id' in values:
            city_val = values['city_id']
            city_id = city_val if isinstance(city_val, (str, int)) else city_val.id
            city_rec = request.env['res.city'].search([('id', '=', city_id)], limit=1)
            distritos = city_rec.get_website_sale_distritos() if city_rec else False

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'tipos_docs': tipos_docs,
            'tipos_comprobantes': tipos_comprobantes,
            'provincias': provincias,
            'distritos': distritos,
        }
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/departamento_infos/<model("res.country.state"):departamento>'], type='json', auth="public", methods=['POST'], website=True)
    def departamento_infos(self, departamento, mode, **kw):
        return dict(
            provincias=[(st.id, st.name, st.l10n_pe_code) for st in departamento.get_website_sale_privincias(mode=mode)],
        )

    @http.route(['/shop/provincia_infos/<model("res.city"):provincia>'], type='json', auth="public", methods=['POST'], website=True)
    def provincia_infos(self, provincia, mode, **kw):
        return dict(
            distritos=[(st.id, st.name, st.code) for st in provincia.get_website_sale_distritos(mode=mode)],
        )

    @http.route(['/shop/buscar/<int:nro>/<string:type>'], type='json', auth="public", methods=['POST'], website=True)
    def buscar_vat(self, nro, type, **kw):
        return dict(
            request.env['res.partner'].consulta_datos_simple(type, nro),
        )

    def checkout_form_validate(self, mode, all_form_values, data):
        error = dict()
        error_message = []

        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]
        country_id = int(data.get('country_id', False) or 0)
        required_fields += mode[1] == 'shipping' and self._get_mandatory_fields_shipping(country_id) or self._get_mandatory_fields_billing(country_id)

        country = request.env['res.country']
        if data.get('country_id'):
            country = country.browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.' + str(error)))

        return error, error_message

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_existe = False
            if 'doc_number' in checkout:
                partner_existe = Partner.sudo().search([('doc_number', '=', checkout['doc_number'])])
            if partner_existe:
                partner_existe.sudo().write(checkout)
                partner_id = partner_existe.id
            else:
                partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return request.redirect('/shop/checkout')
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        for k, v in values.items():
            if k in _PARTNER_WRITABLE_FIELDS and v is not None:
                new_values[k] = v
            else:
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'):
                    _logger.debug("website_sale postprocess: %s value has been dropped", k)

        new_values['team_id'] = request.website.salesteam_id and request.website.salesteam_id.id
        new_values['user_id'] = request.website.salesperson_id and request.website.salesperson_id.id

        if request.website.specific_user_account:
            new_values['website_id'] = request.website.id

        if mode[0] == 'new':
            new_values['company_id'] = request.website.company_id.id

        lang = request.lang.code if request.lang.code in request.website.mapped('language_ids.code') else None
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'

        return new_values, errors, error_msg
