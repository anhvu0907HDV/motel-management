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

    qr_image = fields.Binary(compute="_compute_qr_image", attachment=False)

    @api.depends("payment_method")
    def _compute_qr_image(self):
        for rec in self:
            company = rec.env.company
            if rec.payment_method == "bank":
                rec.qr_image = company.qr_bank_image or False
            elif rec.payment_method == "momo":
                rec.qr_image = company.qr_momo_image or False
            elif rec.payment_method == "vnpay":
                rec.qr_image = company.qr_vnpay_image or False
            else:
                rec.qr_image = False

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be greater than 0.")

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def name_get(self):
        selection_map = dict(self._fields["payment_method"].selection)
        res = []
        for rec in self:
            booking = rec.booking_id.booking_code if rec.booking_id else ""
            method = selection_map.get(rec.payment_method, rec.payment_method)
            amount = rec.amount
            currency = rec.currency_id.name if rec.currency_id else ""
            ref = rec.reference or ""
            parts = [p for p in [booking, method, f"{amount:g} {currency}".strip(), ref] if p]
            name = " / ".join(parts) if parts else f"Payment {rec.id}"
            res.append((rec.id, name))
        return res
