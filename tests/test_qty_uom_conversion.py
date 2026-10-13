# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestQtyUomConversion(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Uom = cls.env['uom.uom']
        cls.pack = Uom.create({'name': 'Pack', 'relative_factor': 1.0})
        cls.box5 = Uom.create({
            'name': 'Box of 5',
            'relative_uom_id': cls.pack.id,
            'relative_factor': 5.0,
        })
        cls.box10 = Uom.create({
            'name': 'Box of 10',
            'relative_uom_id': cls.pack.id,
            'relative_factor': 10.0,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'A4 Copy Paper',
            'is_storable': True,
            'uom_id': cls.pack.id,
            'uom_ids': [(6, 0, [cls.box5.id, cls.box10.id])],
        })

    def test_largest_packaging_split(self):
        self.assertEqual(
            self.product._format_qty_uom_conversion(12.0),
            '1 Box of 10, 2 Pack',
        )

    def test_exact_multiple(self):
        self.assertEqual(
            self.product._format_qty_uom_conversion(10.0),
            '1 Box of 10',
        )

    def test_remainder_only(self):
        self.assertEqual(
            self.product._format_qty_uom_conversion(3.0),
            '3 Pack',
        )

    def test_single_larger_packaging(self):
        self.product.uom_ids = [(6, 0, [self.box10.id])]
        self.assertEqual(
            self.product._format_qty_uom_conversion(12.0),
            '1 Box of 10, 2 Pack',
        )

    def test_no_packaging(self):
        self.product.uom_ids = [(5, 0, 0)]
        self.assertEqual(self.product._format_qty_uom_conversion(12.0), '')

    def test_multiple_packagings_and_loose_remainder(self):
        self.assertEqual(self.product._format_qty_uom_conversion(17),
                         '1 Box of 10, 1 Box of 5, 2 Pack')
        self.assertEqual(self.product._format_qty_uom_conversion(-17),
                         '-1 Box of 10, -1 Box of 5, -2 Pack')
        self.assertEqual(self.product._format_qty_uom_conversion(0), '')

    def test_coke_bottles_boxes_and_ml(self):
        ml = self.env['uom.uom'].create({'name': 'ml', 'rounding': 0.01})
        bottle = self.env['uom.uom'].create({
            'name': 'Bot (250 ml)', 'relative_uom_id': ml.id, 'relative_factor': 250,
        })
        box = self.env['uom.uom'].create({
            'name': 'Box (1250 ml)', 'relative_uom_id': bottle.id, 'relative_factor': 5,
        })
        self.product.write({'uom_id': ml.id, 'uom_ids': [(6, 0, [bottle.id, box.id])]})
        self.assertEqual(self.product._format_qty_uom_conversion(1750),
                         '1 Box (1250 ml), 2 Bot (250 ml)')
        self.assertEqual(self.product._format_qty_uom_conversion(1250), '1 Box (1250 ml)')
        self.assertEqual(self.product._format_qty_uom_conversion(1800.25),
                         '1 Box (1250 ml), 2 Bot (250 ml), 50.25 ml')
        location = self.env['stock.location'].create({
            'name': 'Conversion test', 'usage': 'internal', 'company_id': self.env.company.id,
        })
        quant = self.env['stock.quant'].create({
            'product_id': self.product.id, 'location_id': location.id, 'quantity': 1750,
        })
        self.assertEqual(quant.qty_uom_conversion, '1 Box (1250 ml), 2 Bot (250 ml)')
        self.assertEqual(self.product.with_context(location=location.id).qty_uom_conversion,
                         quant.qty_uom_conversion)
        self.assertEqual(self.product.product_tmpl_id.with_context(location=location.id).qty_uom_conversion,
                         quant.qty_uom_conversion)

    def test_inactive_and_equal_size_packagings(self):
        self.box10.active = False
        self.assertEqual(self.product._format_qty_uom_conversion(17), '3 Box of 5, 2 Pack')
        same = self.box5.copy({'name': 'Other box of 5'})
        self.product.uom_ids = [(6, 0, [self.box5.id, same.id])]
        self.assertEqual(self.product._format_qty_uom_conversion(12), '2 Box of 5, 2 Pack')
