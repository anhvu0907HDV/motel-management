from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelBooking(models.Model):
    _inherit = "motel.booking"

    payment_ids = fields.One2many("motel.payment", "booking_id", string="Payments", readonly=True)

    paid_amount = fields.Monetary(compute="_compute_paid_amount", store=True, currency_field="currency_id")
    remaining_balance = fields.Monetary(compute="_compute_remaining_balance", store=True, currency_field="currency_id")

    @api.depends("payment_ids.amount", "payment_ids.state")
    def _compute_paid_amount(self):
        for rec in self:
            rec.paid_amount = sum(rec.payment_ids.filtered(lambda p: p.state == "posted").mapped("amount"))

    @api.depends("total_amount", "service_total_amount", "paid_amount")
    def _compute_remaining_balance(self):
        for rec in self:
            rec.remaining_balance = (rec.total_amount or 0.0) + (rec.service_total_amount or 0.0) - (rec.paid_amount or 0.0)

    def action_check_out(self):
        for rec in self:
            if rec.remaining_balance and rec.remaining_balance > 0:
                return {
                    "type": "ir.actions.act_window",
                    "name": "Register Payment",
                    "res_model": "motel.payment",
                    "view_mode": "form",
                    "target": "new",
                    "context": {
                        "default_booking_id": rec.id,
                        "default_amount": rec.remaining_balance,
                        "default_payment_method": "cash",
                    },
                }
        return super().action_check_out()
