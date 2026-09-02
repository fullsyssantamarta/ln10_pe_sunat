# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php

import logging
from . import constantes
from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
	_inherit = "sale.order"

	pe_invoice_code = fields.Selection(constantes.COMPROBANTES, 'Tipo de comprobante')

	def pasar_variables_web(self, parametros):
		self.write({
			'pe_invoice_code': parametros['pe_invoice_code'] or False,
		})