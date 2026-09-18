# Stock Unit Conversion Display

Odoo 19 display-only extension for **Inventory → Reporting → Stock**.

Inventory quantity, cost and valuation stay in the product inventory UoM
(`uom_id`). This module adds a **Unit Conversion** column after **Unit**.

## Rule (method B)

1. Main unit = smallest Sales packaging (`uom_ids`) whose factor into `uom_id` is
   strictly greater than 1.
2. Sub unit = remainder in inventory UoM (`uom_id`).
3. Format: `2 Box of 5, 2 Pack`

If several packagings share the same factor, UoM sequence then name decides.

## Examples

| On Hand | Unit | Packagings | Unit Conversion |
|---|---|---|---|
| 12 | Pack | Box of 5, Box of 10 | 2 Box of 5, 2 Pack |
| 12 | bot | Box of 10 | 1 Box of 10, 2 bot |
| 10 | bot | Box of 10 | 1 Box of 10 |
| 3 | bot | Box of 10 | 3 bot |
| 12 | Pack | *(none)* | *(blank)* |

Zero parts are omitted. No packaging → blank.

## Out of scope

Does not change stock moves, reservation, barcodes, purchase UoM, or valuation.
