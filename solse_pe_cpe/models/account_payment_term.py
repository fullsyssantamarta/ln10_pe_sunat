# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError

class AccontPaymentTerm(models.Model):
	_inherit = "account.payment.term"

	tipo_transaccion = fields.Selection([('contado', 'Contado'), ('credito', 'Credito')], string='Tipo de Transacción', default='credito', required=True)