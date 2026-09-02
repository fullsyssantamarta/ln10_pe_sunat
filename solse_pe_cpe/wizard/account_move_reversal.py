# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php

from odoo import models, fields, api, _
import logging
_logging = logging.getLogger(__name__)

class AccountMoveReversal(models.TransientModel):
	_inherit = "account.move.reversal"

	pe_credit_note_code = fields.Selection(selection="_get_pe_crebit_note_type", string="Codigo SUNAT")
	l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Documento', domain=[('code', '=', '07')])
	fecha_nota_credito_proveedor = fields.Date("Fecha emisión del Proveedor")
	payment_reference = fields.Char("Nota de crédito del proveedor")

	@api.model
	def _get_pe_crebit_note_type(self):
		return self.env['pe.datas'].get_selection("PE.CPE.CATALOG9")

	@api.model
	def _get_pe_debit_note_type(self):
		return self.env['pe.datas'].get_selection("PE.CPE.CATALOG10")

	@api.model
	def default_get(self, fields_list):
		res = super().default_get(fields_list)
		if 'l10n_latam_document_type_id' in fields_list and self._context.get('active_model') == 'account.move':
			move_ids = self._context.get('active_ids', [])
			if move_ids:
				move = self.env['account.move'].browse(move_ids[0])
				if move.l10n_latam_document_type_id and move.l10n_latam_document_type_id.nota_credito:
					res['l10n_latam_document_type_id'] = move.l10n_latam_document_type_id.nota_credito.id
		return res

	def reverse_moves(self, **kwargs):
		res = super(AccountMoveReversal, self).reverse_moves(**kwargs)
		if self.env.context.get("is_pe_debit_note", False):
			invoice_domain = res['domain']
			if invoice_domain:
				del invoice_domain[0]
				res['domain'] = invoice_domain
		return res

	def _prepare_default_reversal(self, move):
		res = super()._prepare_default_reversal(move)
		l10n_latam_document_type_id = move.l10n_latam_document_type_id.nota_credito
		res.update({
			'l10n_latam_document_type_id': l10n_latam_document_type_id.id,
			'pe_credit_note_code': self.pe_credit_note_code or move.pe_credit_note_code,
		})
		if move.move_type == 'in_invoice':
			res['fecha_nota_credito_proveedor'] = self.fecha_nota_credito_proveedor
			res['payment_reference'] = self.payment_reference

		return res