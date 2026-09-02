# Plan: Corregir modulo solse_pe_cpe para Odoo 18

## Contexto
El modulo `solse_pe_cpe` maneja el envio de Comprobantes de Pago Electronicos (CPE) a SUNAT (Peru). Las boletas (codigo '03') usan envio asincrono: se agrupan en un Resumen Diario (RC) que se envia a SUNAT y se consulta su estado via ticket. Hay multiples bugs que impiden que este flujo funcione correctamente.

## Problemas identificados y correcciones

### 1. CRITICO: ConditionCode incorrecto en getSummaryDocuments
**Archivo**: [cpe_xml.py:1662](addons/custom/solse_pe_cpe/models/cpe_xml.py#L1662)
**Problema**: Usa `invoice_id.pe_summary_id.is_voided` para determinar ConditionCode. Esto significa que TODAS las boletas en un resumen normal obtienen codigo '1', incluso si fueron anuladas. Y todas en un resumen voided obtienen '3', aunque no lo sean.
**Fix**: Usar `invoice_id.pe_condition_code` del invoice individual:
```python
# Antes:
if invoice_id.pe_summary_id.is_voided:
    ...text = '3'
else:
    ...text = '1'

# Despues:
...text = invoice_id.pe_condition_code or '1'
```

### 2. CRITICO: Campo `number` no existe en Odoo 18
**Archivo**: [solse_cpe.py:406](addons/custom/solse_pe_cpe/models/solse_cpe.py#L406)
**Problema**: `self.invoice_ids[0].number` crashearia en Odoo 18. El campo correcto es `name` o `l10n_latam_document_number`.
**Fix**: Cambiar a `self.invoice_ids[0].l10n_latam_document_number`

### 3. ALTO: Crons no reintentan envios fallidos
**Archivo**: [solse_cpe.py:572-646](addons/custom/solse_pe_cpe/models/solse_cpe.py#L572-L646)
**Problema**: `send_rc()` busca estados `['draft', 'generate', 'verify']` pero cuando un envio falla, el estado queda en `'send'`. Lo mismo para `send_async_cpe()` y `send_async_cpe_nc()` que solo buscan `['generate', 'send']` pero no `'draft'`.
**Fix**:
- `send_rc()`: Agregar `'send'` al dominio de busqueda
- `send_ra()`: Agregar `'send'` al dominio de busqueda
- Para RC/RA con estado 'send' y sin ticket: limpiar xml_document para regenerar

### 4. ALTO: button_annul no maneja resumen en estado intermedio
**Archivo**: [account_move.py:917-924](addons/custom/solse_pe_cpe/models/account_move.py#L917-L924)
**Problema**: Si `pe_summary_id` existe pero su estado no es 'done' (ej: 'draft', 'generate'), la boleta anulada se queda en el resumen original con ConditionCode incorrecto.
**Fix**: Agregar caso `else` - si el resumen aun no fue enviado (draft/generate), la boleta puede quedarse en ese resumen pero su pe_condition_code='3' ya fue seteado. Con el fix #1, el XML usara el pe_condition_code correcto.

### 5. ALTO: Crons silencian excepciones
**Archivo**: [solse_cpe.py:572-646](addons/custom/solse_pe_cpe/models/solse_cpe.py#L572-L646)
**Problema**: Todos los crons usan `except Exception: pass`, haciendo imposible diagnosticar errores.
**Fix**: Agregar logging de errores:
```python
except Exception as e:
    _logging.error("Error en send_rc para CPE %s: %s", cpe_id.name, str(e))
```

### 6. MEDIO: get_cpe_async para RA verifica summary_ids en vez de voided_ids
**Archivo**: [solse_cpe.py:238](addons/custom/solse_pe_cpe/models/solse_cpe.py#L238)
**Problema**: `len(cpe_id.summary_ids.ids) < 500` siempre es True para RA porque los invoices estan en `voided_ids`. No hay limite real.
**Fix**: Verificar el campo correcto segun el tipo:
```python
if type == 'rc':
    ids_to_check = cpe_id.summary_ids
elif type == 'ra':
    ids_to_check = cpe_id.voided_ids
if len(ids_to_check.ids) < 500:
    res = cpe_id
```

### 7. MEDIO: Intervalos de crons demasiado largos
**Archivo**: [tareas_programadas.xml](addons/custom/solse_pe_cpe/data/tareas_programadas.xml)
**Problema**: Los crons de envio de RC/RA corren cada 24 horas. Si el cron ya corrio hoy, las boletas no se envian hasta manana.
**Fix**: Cambiar intervalos:
- `rc_auto_send`: de 1 dia a 2 horas
- `ra_auto_send`: de 1 dia a 4 horas
- `r_consultar_ticket`: de 8 horas a 1 hora
- `sync_auto_send` y `sync_auto_send_nc`: de 1 dia a 4 horas

### 8. MEDIO: write() propaga estado_sunat en cada escritura
**Archivo**: [solse_cpe.py:134-138](addons/custom/solse_pe_cpe/models/solse_cpe.py#L134-L138)
**Problema**: El `write()` override propaga `estado_sunat` a los CPE individuales en CADA escritura, no solo cuando cambia `estado_sunat`.
**Fix**: Solo propagar cuando `estado_sunat` cambio:
```python
def write(self, values):
    res = super().write(values)
    if 'estado_sunat' in values:
        for reg in self.summary_ids:
            if reg.pe_cpe_id:
                reg.pe_cpe_id.estado_sunat = values['estado_sunat']
    return res
```

### 9. MEDIO: _prepare_cpe no regenera XML si ya existe
**Archivo**: [solse_cpe.py:298-304](addons/custom/solse_pe_cpe/models/solse_cpe.py#L298-L304)
**Problema**: Si el XML fue generado pero el envio fallo, un reintento no regenera el XML (condicion `if not self.xml_document`). Para RC/RA que fallaron, si se agregan nuevas boletas al resumen, el XML viejo no las incluye.
**Fix**: En `send_cpe()` para RC/RA, limpiar `xml_document` antes de llamar a `_prepare_cpe()`:
```python
if self.type in ["rc", "ra"]:
    self.xml_document = False  # Forzar regeneracion
    self._prepare_cpe()
    self._sign_cpe()
```

### 10. BAJO: log_cpe.py tiene errores de sintaxis y no esta importado
**Archivo**: [log_cpe.py:44-50](addons/custom/solse_pe_cpe/models/log_cpe.py#L44-L50)
**Problema**: El metodo `ejecturarAcciones` tiene bloques if/elif sin cuerpo (solo comentarios) y usa `error_ids` sin `self.`. El archivo no esta importado en `__init__.py`.
**Fix**: Corregir la sintaxis y agregar `from . import log_cpe` en `__init__.py`. Agregar entradas en `ir.model.access.csv` para los 4 modelos.

### 11. BAJO: send_ra() itera invoice_ids en vez de voided_ids
**Archivo**: [solse_cpe.py:589](addons/custom/solse_pe_cpe/models/solse_cpe.py#L589)
**Problema**: `for invoice_id in cpe_id.invoice_ids` deberia ser `cpe_id.voided_ids`. Funciona por accidente porque `invoice_ids` esta vacio para RA.
**Fix**: Cambiar a `cpe_id.voided_ids`.

## Archivos a modificar

1. **[models/solse_cpe.py](addons/custom/solse_pe_cpe/models/solse_cpe.py)** - Fixes #2, #3, #5, #6, #8, #9, #11
2. **[models/cpe_xml.py](addons/custom/solse_pe_cpe/models/cpe_xml.py)** - Fix #1
3. **[models/account_move.py](addons/custom/solse_pe_cpe/models/account_move.py)** - Fix #4
4. **[models/log_cpe.py](addons/custom/solse_pe_cpe/models/log_cpe.py)** - Fix #10
5. **[models/__init__.py](addons/custom/solse_pe_cpe/models/__init__.py)** - Fix #10
6. **[security/ir.model.access.csv](addons/custom/solse_pe_cpe/security/ir.model.access.csv)** - Fix #10
7. **[data/tareas_programadas.xml](addons/custom/solse_pe_cpe/data/tareas_programadas.xml)** - Fix #7