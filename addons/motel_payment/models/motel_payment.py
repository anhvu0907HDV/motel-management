from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelPayment(models.Model):
    _name = "motel.payment"
    _description = "Motel Payment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "payment_time desc, id desc"

    booking_id = fields.Many2one("motel.booking", required=True, ondelete="restrict", index=True, tracking=True)
    currency_id = fields.Many2one("res.currency", related="booking_id.currency_id", store=True, readonly=True)

    amount = fields.Monetary(required=True, currency_field="currency_id", tracking=True)
    payment_method = fields.Selection(
        [
            ("cash", "Cash"),
            ("bank", "Bank Transfer"),
            ("momo", "MoMo"),
            ("vnpay", "VNPay"),
        ],
        required=True,
        default="cash",
        tracking=True,
    )
    payment_time = fields.Datetime(required=True, default=fields.Datetime.now, index=True, tracking=True)
    reference = fields.Char()
    state = fields.Selection(
        [
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="posted",
        required=True,
        index=True,
        tracking=True,
    )

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be greater than 0.")

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
