# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import fields, models, api, _
import logging
_logging = logging.getLogger(__name__)

class ReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'

	def _prepare_picking_default_values(self):
		res = super(ReturnPicking, self)._prepare_picking_default_values()
		res['origin_id'] = self.picking_id.id
		return res
