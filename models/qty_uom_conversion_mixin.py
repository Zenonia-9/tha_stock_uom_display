# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class QtyUomConversionMixin(models.AbstractModel):
    _name = 'tha.qty.uom.conversion.mixin'
    _description = 'Qty to packaging + remainder formatter'

    def _tha_get_main_packaging_uom(self, inv_uom, packagings):
        """Smallest Sales packaging that holds more than 1 inventory unit."""
        if not inv_uom or not packagings:
            return self.env['uom.uom']

        candidates = []
        for packaging in packagings:
            if packaging == inv_uom:
                continue
            try:
                factor = packaging._compute_quantity(1.0, inv_uom, round=False)
            except Exception:
                continue
            if not factor:
                continue
            if float_compare(factor, 1.0, precision_rounding=inv_uom.rounding) <= 0:
                continue
            candidates.append((
                factor,
                packaging.sequence or 0,
                packaging.name or '',
                packaging,
            ))
        if not candidates:
            return self.env['uom.uom']
        candidates.sort(key=lambda row: (row[0], row[1], row[2]))
        return candidates[0][3]

    def _tha_format_qty_part(self, qty, uom):
        if not uom:
            return ''
        digits = self.env['decimal.precision'].precision_get('Product Unit')
        rounded = float_round(qty, precision_digits=digits)
        if float_is_zero(rounded - int(rounded), precision_digits=digits):
            qty_txt = str(int(rounded))
        else:
            qty_txt = ('%.*f' % (digits, rounded)).rstrip('0').rstrip('.')
        return '%s %s' % (qty_txt, uom.name)

    def _tha_format_qty_uom_conversion(self, qty, inv_uom, packagings):
        if not inv_uom or not packagings:
            return ''
        if qty is False or qty is None:
            return ''

        main_uom = self._tha_get_main_packaging_uom(inv_uom, packagings)
        if not main_uom:
            return ''

        factor = main_uom._compute_quantity(1.0, inv_uom, round=False)
        if not factor or float_compare(factor, 1.0, precision_rounding=inv_uom.rounding) <= 0:
            return ''

        main_qty = float(int(qty / factor))
        sub_qty = float_round(
            qty - (main_qty * factor),
            precision_rounding=inv_uom.rounding,
        )
        if float_is_zero(sub_qty, precision_rounding=inv_uom.rounding):
            sub_qty = 0.0

        parts = []
        if not float_is_zero(main_qty, precision_rounding=main_uom.rounding or 0.01):
            parts.append(self._tha_format_qty_part(main_qty, main_uom))
        if not float_is_zero(sub_qty, precision_rounding=inv_uom.rounding):
            parts.append(self._tha_format_qty_part(sub_qty, inv_uom))
        return ', '.join(parts)
