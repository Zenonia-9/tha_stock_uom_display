# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'tha.qty.uom.conversion.mixin']

    qty_uom_conversion = fields.Char(
        string='Unit Conversion',
        compute='_compute_qty_uom_conversion',
        help='On Hand split into the smallest Sales packaging, then the '
             'inventory unit remainder.',
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
            product.qty_uom_conversion = product._tha_format_qty_uom_conversion(
                product.qty_available, product.uom_id, product.uom_ids,
            )

    def _format_qty_uom_conversion(self, qty):
        """Kept for tests and callers that pass an explicit quantity."""
        self.ensure_one()
        return self._tha_format_qty_uom_conversion(qty, self.uom_id, self.uom_ids)
