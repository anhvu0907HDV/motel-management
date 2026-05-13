from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelRoomType(models.Model):
    _name = "motel.room.type"
    _description = "Motel Room Type"
    _inherit = ["mail.thread", "mail.activity.mixin", "motel.code.mixin", "motel.active.mixin"]

    _sql_constraints = [
        ("motel_room_type_code_uniq", "unique(code)", "Room type code must be unique."),
        ("motel_room_type_name_uniq", "unique(name)", "Room type name must be unique."),
    ]

    name = fields.Char(required=True, tracking=True)
    capacity = fields.Integer(default=1, required=True, tracking=True)
    default_price_hour = fields.Float(tracking=True)
    default_price_night = fields.Float(tracking=True)
    description = fields.Text()

    room_ids = fields.One2many("motel.room", "room_type_id", string="Rooms", readonly=True)

    @api.constrains("capacity")
    def _check_capacity(self):
        for rec in self:
            if rec.capacity < 1:
                raise ValidationError("Capacity must be at least 1.")

    @api.model
    def _motel_sequence_code(self) -> str:
        return "motel.room.type"
