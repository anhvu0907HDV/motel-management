from odoo import api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.motel_base import constants


class MotelRoom(models.Model):
    _name = "motel.room"
    _description = "Motel Room"
    _inherit = ["mail.thread", "mail.activity.mixin", "motel.code.mixin", "motel.active.mixin"]

    _sql_constraints = [
        ("motel_room_code_uniq", "unique(code)", "Room code must be unique."),
        ("motel_room_name_uniq", "unique(name)", "Room name must be unique."),
    ]

    name = fields.Char(required=True, tracking=True)
    floor = fields.Integer(index=True, tracking=True)
    room_type_id = fields.Many2one(
        "motel.room.type", required=True, ondelete="restrict", index=True, tracking=True
    )
    status = fields.Selection(constants.ROOM_STATUSES, default="available", required=True, index=True, tracking=True)
    note = fields.Text()
    status_log_ids = fields.One2many("motel.room.status.log", "room_id", string="Status Logs", readonly=True)

    @api.constrains("floor")
    def _check_floor(self):
        for rec in self:
            if rec.floor is not False and rec.floor < 0:
                raise ValidationError("Floor must be non-negative.")

    def write(self, vals):
        tracked_status_change = "status" in vals
        old_status_by_id = {}
        if tracked_status_change:
            for rec in self:
                old_status_by_id[rec.id] = rec.status

        res = super().write(vals)

        if tracked_status_change:
            for rec in self:
                old_status = old_status_by_id.get(rec.id)
                new_status = rec.status
                if old_status and new_status and old_status != new_status:
                    self.env["motel.room.status.log"].sudo().create(
                        {
                            "room_id": rec.id,
                            "old_status": old_status,
                            "new_status": new_status,
                            "changed_by": self.env.user.id,
                            "note": vals.get("note") or "",
                        }
                    )
        return res

    @api.model
    def _motel_sequence_code(self) -> str:
        return "motel.room"
