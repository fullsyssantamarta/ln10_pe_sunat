# ln10_pe_sunat — Facturación Electrónica SUNAT (Perú) para Odoo 18

Suite de módulos para la emisión de Comprobantes de Pago Electrónicos (CPE)
ante SUNAT: facturas, boletas, notas de crédito/débito, guías de remisión,
resúmenes diarios (RC) y comunicaciones de baja (RA).

## Módulos (familia `solse_pe_cpe`)

| Módulo | Descripción |
|---|---|
| `solse_pe_cpe` | Núcleo CPE SUNAT (generación, firma y envío de XML UBL 2.1) |
| `solse_pe_cpe_dev` | Herramientas / asistentes (agrupar boletas, etc.) |
| `solse_pe_cpe_guias` | Guías de remisión electrónicas |
| `solse_pe_cpe_log` | Registro (log) de operaciones CPE |
| `solse_pe_cpe_pos` | Emisión CPE desde el Punto de Venta |
| `solse_pe_cpe_public` | Portal / web pública de comprobantes |
| `solse_pe_cpe_purchase` | Comprobantes en Compras |
| `solse_pe_cpe_report` | Reportes CPE |
| `solse_pe_cpe_sale` | Comprobantes en Ventas |
| `solse_pe_cpe_web` | Facturación desde la tienda web |

## Instalación

Copiar los módulos a la carpeta de addons de Odoo (p. ej. `/mnt/extra-addons/custom`),
actualizar la lista de aplicaciones e instalar `solse_pe_cpe`. Las extensiones
(`_pos`, `_sale`, `_purchase`, etc.) se instalan según se necesiten.

## Requisitos

- Odoo 18
- Certificado digital SUNAT (se carga en la base de datos, **no** en el código)
- Credenciales SOL de la empresa

## Notas

- Los certificados y credenciales se gestionan desde Odoo y **no** forman parte
  de este repositorio.
- Resumen diario (RC): la `FechaGeneracion` del XML coincide con la fecha del
  nombre del archivo (fecha de generación), mientras que la `FechaReferencia`
  corresponde a la fecha de emisión de las boletas.
