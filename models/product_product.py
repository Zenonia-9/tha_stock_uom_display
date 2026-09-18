# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_uom_conversion = fields.Char(
        string='Unit Conversion',
        compute='_compute_qty_uom_conversion',
        help='On Hand split into the smallest Sales packaging, then the '
             'inventory unit remainder. Example: 12 Pack with Box of 5 '
             '→ "2 Box of 5, 2 Pack".',
    )

    @api.depends(
        'qty_available',
        'uom_id',
        'uom_id.factor',
        'uom_id.rounding',
        'uom_id.name',
        'uom_ids',
        'uom_ids.factor',
        'uom_ids.sequence',
        'uom_ids.name',
    )
    @api.depends_context(
        'warehouse_id',
        'location',
        'location_id',
        'to_date',
        'from_date',
        'company_id',
        'allowed_company_ids',
    )
    def _compute_qty_uom_conversion(self):
        for product in self:
            product.qty_uom_conversion = product._format_qty_uom_conversion(
                product.qty_available,
            )

    def _get_main_packaging_uom(self):
        """Smallest Sales packaging that holds more than 1 inventory unit.

        Method B: among ``uom_ids``, pick the packaging whose quantity in
        ``uom_id`` is the smallest value strictly greater than 1. Ties use
        UoM sequence then name.
        """
        self.ensure_one()
        inv_uom = self.uom_id
        if not inv_uom or not self.uom_ids:
            return self.env['uom.uom']

        candidates = []
        for packaging in self.uom_ids:
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

    def _split_qty_main_sub(self, qty):
        """Return (main_qty, main_uom, sub_qty, sub_uom) for qty in uom_id."""
        self.ensure_one()
        sub_uom = self.uom_id
        main_uom = self._get_main_packaging_uom()
        if not sub_uom or not main_uom or qty is False or qty is None:
            return 0.0, main_uom, qty or 0.0, sub_uom

        factor = main_uom._compute_quantity(1.0, sub_uom, round=False)
        if not factor or float_compare(factor, 1.0, precision_rounding=sub_uom.rounding) <= 0:
            return 0.0, main_uom, qty, sub_uom

        main_qty = float(int(qty / factor))  # toward zero for negatives
        sub_qty = qty - (main_qty * factor)
        sub_qty = float_round(sub_qty, precision_rounding=sub_uom.rounding)
        if float_is_zero(sub_qty, precision_rounding=sub_uom.rounding):
            sub_qty = 0.0
        return main_qty, main_uom, sub_qty, sub_uom

    def _format_qty_part(self, qty, uom):
        if not uom:
            return ''
        digits = self.env['decimal.precision'].precision_get('Product Unit')
        rounded = float_round(qty, precision_digits=digits)
        if float_is_zero(rounded - int(rounded), precision_digits=digits):
            qty_txt = str(int(rounded))
        else:
            qty_txt = ('%.*f' % (digits, rounded)).rstrip('0').rstrip('.')
        return '%s %s' % (qty_txt, uom.name)

    def _format_qty_uom_conversion(self, qty):
        self.ensure_one()
        if not self.uom_id or not self.uom_ids:
            return ''
        if qty is False or qty is None:
            return ''

        main_qty, main_uom, sub_qty, sub_uom = self._split_qty_main_sub(qty)
        parts = []
        if main_uom and not float_is_zero(
            main_qty, precision_rounding=main_uom.rounding or 0.01,
        ):
            parts.append(self._format_qty_part(main_qty, main_uom))
        if sub_uom and not float_is_zero(
            sub_qty, precision_rounding=sub_uom.rounding,
        ):
            parts.append(self._format_qty_part(sub_qty, sub_uom))
        return ', '.join(parts)
