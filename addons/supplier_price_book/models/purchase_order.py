from odoo import models, fields
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    # (US №4)
    _inherit = 'purchase.order'

    def action_update_schedule(self):
        # кнопка "Обновить график": уведдение цеха о новом сроке прихода сырья
        for order in self:
            if order.state not in ('purchase', 'done'):
                raise UserError('Обновлять график можно только у подтверждённого заказа.')
            dates = [d for d in order.order_line.mapped('date_planned') if d]
            if not dates:
                raise UserError('У строк заказа не заданы плановые даты прихода.')
            latest = max(dates)
            # перевод даты из UTC в часовой пояс пользователя для сообщения
            latest_local = fields.Datetime.context_timestamp(order, latest)
            order.message_post(
                body='График поставки обновлён. Новый ожидаемый срок прихода сырья: %s'
                     % latest_local.strftime('%d.%m.%Y %H:%M')
            )
        return True
