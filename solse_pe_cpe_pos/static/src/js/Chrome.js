
odoo.define('solse_pe_cpe_pos.Chrome', function(require) {
    'use strict';

    const { _t } = require('web.core');
    const { getDataURLFromFile } = require('web.utils');
    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
	const rpc = require('web.rpc');

    const ChromeCPE = (Chrome) =>
		class extends Chrome {
			async start() {
	            await super.start();
	        }
	        get imageUrl() {
	        	let ruta_logo = '/web/binary/company_logo';
            	return ruta_logo;
            }
	    };

    Registries.Component.extend(Chrome, ChromeCPE);

    return Chrome;
});
