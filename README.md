# Stock Unit Conversion Display

Odoo 19 display-only extension. Inventory quantity, cost and valuation stay in
the product inventory UoM (`uom_id`). **Unit Conversion** shows the same quantity
split into the smallest Sales packaging plus remainder.

## Rule (method B)

1. Main unit = smallest Sales packaging (`uom_ids`) whose factor into `uom_id` is
   strictly greater than 1.
2. Sub unit = remainder in inventory UoM (`uom_id`).
3. Format: `2 Box of 5, 2 Pack`

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
| 12 | Pack | Box of 5, Box of 10 | 2 Box of 5, 2 Pack |
| 12 | bot | Box of 10 | 1 Box of 10, 2 bot |
| 10 | bot | Box of 10 | 1 Box of 10 |
| 3 | bot | Box of 10 | 3 bot |
| 12 | Pack | *(none)* | *(blank)* |
