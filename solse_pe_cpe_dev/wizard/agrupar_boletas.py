from odoo import models, fields, _
from odoo.exceptions import UserError


class AgruparResumen(models.TransientModel):
	_name = "solse.agrupar.resumen"
	_description = "Agrupar boletas en resumen"

	force_post = fields.Boolean(string="Force", help="Entries in the future are set to be auto-posted by default. Check this checkbox to post them now.")

	def crear_resumen_cpe(self):
		comprobantes = self.env['solse.cpe'].browse(self._context.get('active_ids', []))
		for reg in comprobantes:
			if reg.estado_sunat not in ['01', '07', '09']:
				continue
			invoice_id = reg.invoice_ids[0]
			if not invoice_id:
				raise UserError('No se encontro un comprobante dentro de %s' % reg.name)
			
			if invoice_id.pe_invoice_code != '03':
				continue
			pe_summary_id = self.env['solse.cpe'].get_cpe_async('rc', invoice_id)
			invoice_id.pe_summary_id = pe_summary_id.id

		return {'type': 'ir.actions.act_window_close'}
