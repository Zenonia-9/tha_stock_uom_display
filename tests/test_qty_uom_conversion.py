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

    def test_smallest_packaging_split(self):
        self.assertEqual(
            self.product._format_qty_uom_conversion(12.0),
            '2 Box of 5, 2 Pack',
        )

    def test_exact_multiple(self):
        self.assertEqual(
            self.product._format_qty_uom_conversion(10.0),
            '2 Box of 5',
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
