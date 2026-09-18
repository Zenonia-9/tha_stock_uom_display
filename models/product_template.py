# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'tha.qty.uom.conversion.mixin']

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
        for template in self:
            template.qty_uom_conversion = template._tha_format_qty_uom_conversion(
                template.qty_available, template.uom_id, template.uom_ids,
            )
