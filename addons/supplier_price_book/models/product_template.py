from odoo import models, fields, api


class ProductTemplate(models.Model):
    # расширение стандартной модели товара, а не создание новой
    _inherit = 'product.template'

    cheapest_supplier_id = fields.Many2one(
        'res.partner',
        string='Самый дешёвый поставщик',
        compute='_compute_cheapest_supplier',
        store=False,
    )
    cheapest_supplier_price = fields.Float(
        string='Мин. цена закупки',
        compute='_compute_cheapest_supplier',
        store=False,
    )

    @api.depends('seller_ids.price', 'seller_ids.partner_id')
    def _compute_cheapest_supplier(self):
        for product in self:
            # seller_ids, стандартный список поставщиков (product.supplierinfo)
            sellers = product.seller_ids.sorted(key=lambda s: s.price)
            if sellers:
                product.cheapest_supplier_id = sellers[0].partner_id
                product.cheapest_supplier_price = sellers[0].price
            else:
                product.cheapest_supplier_id = False
                product.cheapest_supplier_price = 0.0
