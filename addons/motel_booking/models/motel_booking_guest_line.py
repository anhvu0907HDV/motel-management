from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelBookingGuestLine(models.Model):
    _name = "motel.booking.guest.line"
    _description = "Motel Booking Guest Line"
    _order = "is_primary desc, id asc"

    booking_id = fields.Many2one("motel.booking", required=True, ondelete="cascade", index=True)
    guest_id = fields.Many2one("motel.guest", required=True, ondelete="restrict", index=True)
    is_primary = fields.Boolean(default=False)
    checkin_time = fields.Datetime(default=lambda self: self.env.context.get("default_checkin_time"))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.booking_id:
                continue
            primaries = rec.booking_id.guest_line_ids.filtered("is_primary")
            if not primaries and len(rec.booking_id.guest_line_ids) == 1:
                rec.is_primary = True
        return records

    @api.constrains("is_primary", "booking_id")
    def _check_single_primary(self):
        for rec in self:
            if not rec.booking_id:
                continue
            primaries = rec.booking_id.guest_line_ids.filtered("is_primary")
            if len(primaries) > 1:
                raise ValidationError("Only one guest line can be marked as primary.")
