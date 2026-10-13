# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockQuant(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant', 'tha.qty.uom.conversion.mixin']

    qty_uom_conversion = fields.Char(
        string='Unit Conversion',
        compute='_compute_qty_uom_conversion',
        help='On Hand split into Sales packagings from largest to smallest, then the '
             'inventory unit remainder.',
    )

    @api.depends(
        'quantity',
        'product_id',
        'product_id.uom_id',
        'product_id.uom_id.factor',
        'product_id.uom_id.rounding',
        'product_id.uom_id.name',
        'product_id.uom_ids',
        'product_id.uom_ids.factor',
        'product_id.uom_ids.active',
        'product_id.uom_ids.sequence',
        'product_id.uom_ids.name',
    )
    def _compute_qty_uom_conversion(self):
        for quant in self:
            product = quant.product_id
            if not product:
                quant.qty_uom_conversion = ''
                continue
            quant.qty_uom_conversion = quant._tha_format_qty_uom_conversion(
                quant.quantity, product.uom_id, product.uom_ids,
            )
