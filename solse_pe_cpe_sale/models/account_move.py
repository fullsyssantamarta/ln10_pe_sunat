# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.


from odoo import api, fields, models,_
from odoo.exceptions import UserError
import logging
_logging = logging.getLogger(__name__)

class InheritedSaleOrder(models.Model):
	_inherit = 'account.move'

	venta_id = fields.Many2one("sale.order", "Venta id")
	orden_compra = fields.Char("Orden de compra")

	descuento_global = fields.Boolean("Aplicar descuento Global")
	amount_discount = fields.Monetary(string='Descuento', store=True, readonly=True, compute='_compute_amount', tracking=True)

	@api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
	def supply_rate(self):
		for inv in self:
			if not inv.descuento_global:
				return
			elif inv.discount_type == 'percent':
				for line in inv.line_ids:
					line.discount = inv.discount_rate
			else:
				total = discount = 0.0
				for line in inv.invoice_line_ids:
					total += (line.quantity * line.price_unit)
				if inv.discount_rate != 0:
					discount = (inv.discount_rate / total) * 100
				else:
					discount = inv.discount_rate
				for line in inv.line_ids:
					line.discount = discount

			# inv._compute_tax_totals_json()  # No existe en Odoo 18, se calcula automáticamente