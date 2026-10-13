# -*- coding: utf-8 -*-

import math

from odoo import models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class QtyUomConversionMixin(models.AbstractModel):
    _name = 'tha.qty.uom.conversion.mixin'
    _description = 'Qty to packaging + remainder formatter'

    def _tha_get_packaging_uoms(self, inv_uom, packagings):
        """Packaging conversions ordered from largest to smallest."""
        if not inv_uom or not packagings:
            return []

        candidates = []
        for packaging in packagings:
            if packaging == inv_uom or not packaging.active:
                continue
            try:
                factor = packaging._compute_quantity(1.0, inv_uom, round=False)
            except Exception:
                continue
            if not math.isfinite(factor):
                continue
            if float_compare(factor, 1.0, precision_rounding=inv_uom.rounding) <= 0:
                continue
            candidates.append((
                factor,
                packaging.sequence or 0,
                packaging.name or '',
                packaging,
            ))
        candidates.sort(key=lambda row: (-row[0], row[1], row[2], row[3].id))
        return [(row[0], row[3]) for row in candidates]

    def _tha_get_main_packaging_uom(self, inv_uom, packagings):
        candidates = self._tha_get_packaging_uoms(inv_uom, packagings)
        return candidates[0][1] if candidates else self.env['uom.uom']

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

        candidates = self._tha_get_packaging_uoms(inv_uom, packagings)
        if not candidates:
            return ''

        sign = -1 if qty < 0 else 1
        remaining = float_round(abs(qty), precision_rounding=inv_uom.rounding)
        parts = []
        for factor, packaging in candidates:
            whole = int(remaining / factor)
            # Avoid losing an exact package to floating-point conversion noise.
            if float_is_zero(remaining - (whole + 1) * factor,
                             precision_rounding=inv_uom.rounding):
                whole += 1
            if not whole:
                continue
            parts.append(self._tha_format_qty_part(sign * whole, packaging))
            remaining = float_round(remaining - whole * factor,
                                    precision_rounding=inv_uom.rounding)
            if float_is_zero(remaining, precision_rounding=inv_uom.rounding):
                remaining = 0.0
                break
        if not float_is_zero(remaining, precision_rounding=inv_uom.rounding):
            parts.append(self._tha_format_qty_part(sign * remaining, inv_uom))
        return ', '.join(parts)
