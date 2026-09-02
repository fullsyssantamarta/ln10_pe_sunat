# -*- coding: utf-8 -*-
{
	'name': "Perú: Compras",

	'summary': """
		Enlace del modulo de compras con la creacion de facturas usando el tipo de documento correspondiente""",

	'description': """
		Facturación - Perú
		Enlace del modulo de compras con la creacion de facturas usando el tipo de documento correspondiente
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",
	'category': 'Financial',
	'version': '18.0.1.0',
	'license': 'LGPL-3',

	'depends': [
		'solse_pe_edi',
		'solse_pe_cpe',
		'purchase',
	],
	'data': [
		'views/detalle_compras_view.xml',
	],
	'installable': True,
	'price': 60,
	'currency': 'USD',
}