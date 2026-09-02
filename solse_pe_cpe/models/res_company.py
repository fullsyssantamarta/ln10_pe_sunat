# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php

from odoo import api, fields, models, _


class Company(models.Model):
	_inherit = "res.company"

	pe_is_sync = fields.Boolean("Es sincrono", default=True)
	pe_certificate_id = fields.Many2one(comodel_name="cpe.certificate", string="Certificado", domain="[('state','=','done')]")
	pe_cpe_server_id = fields.Many2one(comodel_name="cpe.server", string="Servidor", domain="[('state','=','done')]")
	enviar_email = fields.Boolean('Envio correo automatico', help="Si esta activo cada vez que se confirme un comprobante se enviara el pdf al cliente")