# Stock Unit Conversion Display

Odoo 19 display-only extension. Inventory quantity, cost and valuation stay in
the product inventory UoM (`uom_id`). **Unit Conversion** shows the same quantity
split into Sales packagings from largest to smallest, plus any inventory-unit remainder.

## Rule

1. Read active Sales packagings (`uom_ids`) whose conversion into `uom_id` is
   strictly greater than 1, ordered by size from largest to smallest.
2. Show whole packages of each size, using each remaining quantity for the next size.
3. Show any loose remainder in inventory UoM (`uom_id`). When no usable packaging
   conversions exist, show the full quantity in inventory UoM. Zero quantities are omitted.
4. Negative quantities use the same breakdown with negative counts.

## Views (on-hand only)

- Inventory → Reporting → Stock
- Inventory → Reporting → Locations (list + form)
- Inventory → Operations → Physical Inventory
- Inventory → Products → Products / Product Variants lists
- Product form (next to On Hand)
- Product kanban

Not added on stock moves, pickings, sales, or purchase lines.

## Examples

| On Hand | Unit | Packagings | Unit Conversion |
|---|---|---|---|
| 12 | Pack | Box of 5, Box of 10 | 1 Box of 10, 2 Pack |
| 17 | Pack | Box of 5, Box of 10 | 1 Box of 10, 1 Box of 5, 2 Pack |
| 1750 | ml | Bot (250 ml), Box (1250 ml) | 1 Box (1250 ml), 2 Bot (250 ml) |
| 12 | bot | Box of 10 | 1 Box of 10, 2 bot |
| 10 | bot | Box of 10 | 1 Box of 10 |
| 3 | bot | Box of 10 | 3 bot |
| 12 | Pack | *(none)* | 12 Pack |

## Validation (2026-10-13, version 19.0.1.2.1)

Python/XML syntax and manifest data paths checked. Upgraded in THA, ran all eight
module tests successfully, restarted Odoo and inspected the project runtime log.
Checks cover multiple sizes, exact packages, loose and fractional remainders,
negative quantities, inactive packaging, equal-size packaging and the quant,
product and template computed fields.

Authenticated HTTP reads of existing Coke lines confirmed:

- YGN/Stock, 1750 ml: `1 Box (1250 ml), 2 Bot (250 ml)`.
- YGN/Stock/Ahlone, 1250 ml: `1 Box (1250 ml)`.

This verification performed no writes to ordinary inventory records.
