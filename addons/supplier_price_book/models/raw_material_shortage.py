from odoo import models, fields, api
from odoo.exceptions import UserError


class RawMaterialShortage(models.Model):
    _name = 'raw.material.shortage'
    _description = 'Дефицит сырья'

    product_id = fields.Many2one('product.product', string='Материал', required=True)
    qty_on_hand = fields.Float(string='Текущий остаток')
    qty_required = fields.Float(string='Необходимый объём')
    qty_to_order = fields.Float(
        string='Заказать',
        compute='_compute_qty_to_order',
        store=True,
    )

    @api.depends('qty_required', 'qty_on_hand')
    def _compute_qty_to_order(self):
        for rec in self:
            rec.qty_to_order = max(rec.qty_required - rec.qty_on_hand, 0.0)

    def action_recompute(self):
        # Пересобрать список дефицита по открытым производственным заказам.
        self.search([]).unlink()
        productions = self.env['mrp.production'].search([
            ('state', 'in', ('confirmed', 'progress', 'to_close')),
        ])
        demand = {}
        for mo in productions:
            for move in mo.move_raw_ids:
                demand[move.product_id.id] = demand.get(move.product_id.id, 0.0) + move.product_uom_qty
        rows = []
        for product_id, required in demand.items():
            product = self.env['product.product'].browse(product_id)
            on_hand = product.qty_available
            if required > on_hand:
                rows.append({
                    'product_id': product_id,
                    'qty_on_hand': on_hand,
                    'qty_required': required,
                })
        self.create(rows)
        return True

    def action_order(self):
        # Кнопка "Заказать": создать черновик заказа поставщику и открыть его
        self.ensure_one()
        sellers = self.product_id.seller_ids.sorted(key=lambda s: s.price)
        if not sellers:
            raise UserError('У материала не задан поставщик. Добавьте поставщика в карточке товара (US №3).')
        seller = sellers[0]
        order = self.env['purchase.order'].create({
            'partner_id': seller.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'name': self.product_id.display_name,
                'product_qty': self.qty_to_order,
                'product_uom_id': self.product_id.uom_id.id,
                'date_planned': fields.Datetime.now(),
            })],
        })
        return {
            'name': 'Заказ поставщику',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }
