from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelService(models.Model):
    _name = "motel.service"
    _description = "Motel Service"
    _inherit = ["mail.thread", "mail.activity.mixin", "motel.code.mixin", "motel.active.mixin"]

    _sql_constraints = [
        ("motel_service_code_uniq", "unique(code)", "Service code must be unique."),
        ("motel_service_name_uniq", "unique(name)", "Service name must be unique."),
    ]

    name = fields.Char(required=True, tracking=True)
    price = fields.Float(required=True, tracking=True)
    category = fields.Selection(
        [
            ("food", "Food"),
            ("drink", "Drink"),
            ("laundry", "Laundry"),
            ("other", "Other"),
        ],
        default="other",
        required=True,
        index=True,
        tracking=True,
    )

    @api.model
    def _motel_sequence_code(self) -> str:
        return "motel.service"

    @api.constrains("price")
    def _check_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError("Service price must be non-negative.")
