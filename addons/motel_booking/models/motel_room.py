from odoo import api, fields, models


class MotelRoom(models.Model):
    _inherit = "motel.room"

    current_booking_id = fields.Many2one(
        "motel.booking",
        string="Current Booking",
        ondelete="set null",
        index=True,
        readonly=True,
    )

    current_checkin_time = fields.Datetime(related="current_booking_id.checkin_time", readonly=True)
    current_primary_guest_id = fields.Many2one(
        "motel.guest",
        compute="_compute_current_primary_guest_id",
        readonly=True,
    )

    @api.depends("current_booking_id", "current_booking_id.guest_line_ids.is_primary", "current_booking_id.guest_line_ids.guest_id")
    def _compute_current_primary_guest_id(self):
        for rec in self:
            booking = rec.current_booking_id
            if not booking:
                rec.current_primary_guest_id = False
                continue
            primary_line = booking.guest_line_ids.filtered("is_primary")[:1]
            rec.current_primary_guest_id = primary_line.guest_id if primary_line else False
