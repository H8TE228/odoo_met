from odoo import models, fields
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    # Расширяем стандартный заказ поставщику (US №4 и US №5).
    _inherit = 'purchase.order'

    def action_update_schedule(self):
        # US4. Кнопка "Обновить график": уведомить цех о новом сроке прихода сырья.
        for order in self:
            if order.state not in ('purchase', 'done'):
                raise UserError('Обновлять график можно только у подтверждённого заказа.')
            dates = [d for d in order.order_line.mapped('date_planned') if d]
            if not dates:
                raise UserError('У строк заказа не заданы плановые даты прихода.')
            latest = max(dates)
            latest_local = fields.Datetime.context_timestamp(order, latest)
            order.message_post(
                body='График поставки обновлён. Новый ожидаемый срок прихода сырья: %s'
                     % latest_local.strftime('%d.%m.%Y %H:%M')
            )
        return True

    def action_create_return(self):
        # US5. Кнопка "Оформить возврат": вернуть некондиционное сырьё поставщику.
        self.ensure_one()
        receipts = self.picking_ids.filtered(
            lambda p: p.state == 'done' and p.picking_type_id.code == 'incoming'
        )
        if not receipts:
            raise UserError('Нет подтверждённого прихода по этому заказу - возвращать нечего.')
        wizard = self.env['stock.return.picking'].create({'picking_id': receipts[0].id})
        # Проставляем количество к возврату (по умолчанию мастер ставит 0).
        for line in wizard.product_return_moves:
            line.quantity = line.move_id.product_uom_qty
        return_action = wizard.action_create_returns()
        # После возврата остаток снизится - пересобираем дефицит (связь с US №1).
        self.env['raw.material.shortage'].action_recompute()
        return return_action
