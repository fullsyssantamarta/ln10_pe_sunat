# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api,models

class GuideReport(models.AbstractModel):
	_name = "report.solse_guias_facturabien.guide_mov_template"
	_description = 'Reporte de guia'

	@api.model
	def get_report_values(self,docids,data=None):

		records = self.env[objectname].browse(docids)
		return {
			"doc_ids":docids,
			"docs":records,
			"data":data,
		}