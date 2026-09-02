# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php

from odoo import http
from odoo.http import request
import re
import logging
_logging = logging.getLogger(__name__)


class WebPeCpe(http.Controller):
	@http.route('/facturas/', type='http', auth='public', website=True)
	def render_cpe_page(self, **kw):
		if request.httprequest.method == 'POST':
			try:
				req = request.httprequest.form
				company_id = request.website.company_id
				doc_type = (not req.get('doc_type') or req.get('doc_type') == "-") and False or req.get('doc_type')
				doc_number = (not req.get('doc_number') or req.get('doc_number') == "-") and False or req.get('doc_number') or False
				numero = req.get('number', '')
				if not numero or not re.match(r'^(B|F){1}[A-Z0-9]{3}\-\d+$', numero):
					return request.render('solse_pe_cpe_public.cpe_page_reponse', {'invoice': {'error': True}})
				num = numero.split("-")
				partner_obj = request.env['res.partner']
				if doc_number and doc_type == '6':
					if not partner_obj.validate_ruc(doc_number):
						return request.render('solse_pe_cpe_public.cpe_page_reponse', {'invoice': {'error': True}})
				if doc_number and doc_type == '1':
					if len(doc_number) != 8:
						return request.render('solse_pe_cpe_public.cpe_page_reponse', {'invoice': {'error': True}})

				query_buscar = [
					('pe_invoice_code', '=', req.get('document_type')),
					('partner_id.doc_type', '=', doc_type),
					('partner_id.doc_number', '=', doc_number),
					('invoice_date', '=', req.get('date_invoice')),
					('name', 'ilike', "%s-%s" % (num[0], num[1])),
					('amount_total', '=', req.get('amount_total')),
					('company_id.partner_id.vat', '=', company_id.vat),
				]
				invoice = request.env['account.move'].sudo().search(query_buscar)
				res = invoice and invoice.sudo().get_public_cpe() or {}
				return request.render('solse_pe_cpe_public.cpe_page_reponse', {'invoice': res})
			except Exception:
				return request.render('solse_pe_cpe_public.cpe_page_reponse', {'invoice': {'error': True}})
		return request.render('solse_pe_cpe_public.cpe_page', {})
