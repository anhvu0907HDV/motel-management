import time

from psycopg2 import DatabaseError

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger


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
    current_primary_guest_phone = fields.Char(
        compute="_compute_current_primary_guest_phone",
        readonly=True,
    )
    current_primary_guest_identity_number = fields.Char(
        compute="_compute_current_primary_guest_identity_number",
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

    @api.depends("current_primary_guest_id", "current_primary_guest_id.phone")
    def _compute_current_primary_guest_phone(self):
        for rec in self:
            rec.current_primary_guest_phone = rec.current_primary_guest_id.phone or False

    @api.depends("current_primary_guest_id", "current_primary_guest_id.identity_number")
    def _compute_current_primary_guest_identity_number(self):
        for rec in self:
            rec.current_primary_guest_identity_number = rec.current_primary_guest_id.identity_number or False

    def _quick_set_status(self, new_status: str):
        attempts = 3
        for i in range(attempts):
            try:
                with self.env.cr.savepoint(flush=False), mute_logger("odoo.sql_db"):
                    for rec in self:
                        if rec.current_booking_id:
                            raise ValidationError(
                                "This room has an active booking. Please check-out/cancel the booking before changing room status."
                            )
                        rec.status = new_status
                return True
            except DatabaseError as e:
                # 40001 SerializationFailure
                if getattr(e, "pgcode", None) != "40001" or i >= attempts - 1:
                    raise
                time.sleep(0.1 * (i + 1))

    def action_quick_set_available(self):
        return self._quick_set_status("available")

    def action_quick_set_cleaning(self):
        return self._quick_set_status("cleaning")

    def action_quick_set_maintenance(self):
        return self._quick_set_status("maintenance")
