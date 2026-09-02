# 08/09/2022
* Se agrega filtro para entorno multiempresa en de certificado y servidor dentro de la empresa.
* Se mejora filtro en lineas de factura de venta, el tipo de impuesto de venta ya no se muestra en facturas de compra

# 13/09/2022
* Se establece un codigo de producto para el xml en caso el producto no cuente con uno y asi evitar enviar "-" que actualmente "devuelve aceptado con observaciones"
* Se actualiza la funcion "_ agregar_informacion_empresa" para tomar los datos desde una funcion, esto sirve para el modulo de multisucursal

* Se agrega configuracion para poder visualizar los montos totales de exonerados y demas tanto en el formulario como en la impresion (se tiene que modificar el grupo de tipo de impuesto activando el check "Mostrar base" de los registros que se requieran)

# 14/09/2022
* Se mejora la visualizacion del tipo de cambio dolar en la factura

# 02/10/2022
* Se arregla bug con el codigo de producto que se envia en el xml
* Se arregla bug que se tenia en algunos casos con el redondeo de la detracciones que se envia en el xml

# 07/10/2022
* Se arregla bug al ocultar/mostrar el tipo de documento en factura cuando se ingresa desde ventas

# 14/10/2022
* Se modifica reporte de factura para enlazar mejor con el modulo de guias electronicas

# 17/10/2022
* Se soluciona bug al emitir notas de detraccion en soles (se vio despues de la actualizacion de pagos detracion en dolares)

# 17/10/2022
* Se agrega etiqueta Type en el envio de clave para que sea admitido por OSE.
* Se mejora la visualizacion del tipo de pago credito, ahora muestra el nombre del plazo de pago seleccionado.

# 18/10/2022
* Se soluciona bug en la impresion del pdf cuando la factura es en dolares (salio con la actualizacion para visualizar las diferentes opereciones)

# 21/10/2022
* Se mejora visualizacion de descuento cuanto tiene muchos decimales
* Se aumenta el ancho del campo "Número" y "Cliente" en la vista lista de Facturas

# 24/10/2022
* Se mejora visualizacion de montos de retención.

# 30/11/2022
* Se soluciona bug en notas de credito que tenian como origen facturas con descuento.

# 10/11/2022
* Se soluciona bug al visualizar monto de operacion gravada cuando es en dolares

# 23/12/2022
* Se agrega campo que se usara en el modulo solse_pe_cpe_pos_offline y que sirve para gestionar facturas creadas en modo offline

# 27/12/2022
* Se agrega función para validación de envió, útil para otros módulos que dependen de este.

# 06/12/2022
* Se soluciona bug al emitir notas de credito con items con cantidades mayores a 1.

# 22/02/2023
* Se soluciona bug que se tenia para algunos casos con el uso de impuesto a la bolsa

# 28/02/2023
* Se mejora validacion para facturas de exportacion

# 13/03/2032
* Se mejora validacion para facturas de exportacion en el xml

# 11/05/223
* Se agrega configuracion de url de consulta para tomar en cuenta paso con conexion a OSE para consulta de cdr