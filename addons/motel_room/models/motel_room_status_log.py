from odoo import fields, models

from odoo.addons.motel_base import constants


class MotelRoomStatusLog(models.Model):
    _name = "motel.room.status.log"
    _description = "Motel Room Status Log"
    _order = "changed_at desc, id desc"

    room_id = fields.Many2one("motel.room", required=True, ondelete="cascade", index=True)
    old_status = fields.Selection(constants.ROOM_STATUSES, required=True, index=True)
    new_status = fields.Selection(constants.ROOM_STATUSES, required=True, index=True)
    changed_by = fields.Many2one("res.users", required=True, ondelete="restrict", index=True)
    changed_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    note = fields.Text()
