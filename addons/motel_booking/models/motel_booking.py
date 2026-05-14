from odoo import api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.motel_base import constants


class MotelBooking(models.Model):
    _name = "motel.booking"
    _description = "Motel Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "checkin_time desc, id desc"

    name = fields.Char(required=True, copy=False, tracking=True)
    booking_code = fields.Char(required=True, default="New", copy=False, index=True, readonly=True)

    room_id = fields.Many2one("motel.room", required=True, ondelete="restrict", index=True, tracking=True)

    checkin_time = fields.Datetime(required=True, default=fields.Datetime.now, index=True, tracking=True)
    expected_checkout = fields.Datetime(index=True, tracking=True)
    checkout_time = fields.Datetime(index=True, tracking=True)

    duration_hour = fields.Float(compute="_compute_duration_hour", store=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("checked_in", "Checked In"),
            ("checked_out", "Checked Out"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        index=True,
        tracking=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    total_amount = fields.Monetary(currency_field="currency_id", tracking=True)
    service_total_amount = fields.Monetary(
        compute="_compute_service_total_amount",
        currency_field="currency_id",
    )
    deposit_amount = fields.Monetary(currency_field="currency_id", tracking=True)
    note = fields.Text()

    room_price_hour_snapshot = fields.Float(readonly=True)
    room_price_night_snapshot = fields.Float(readonly=True)

    guest_line_ids = fields.One2many("motel.booking.guest.line", "booking_id", string="Guests")
    service_line_ids = fields.One2many("motel.booking.service.line", "booking_id", string="Services")

    @api.depends("service_line_ids.subtotal")
    def _compute_service_total_amount(self):
        for rec in self:
            rec.service_total_amount = sum(rec.service_line_ids.mapped("subtotal"))

    def _next_booking_code(self) -> str:
        return self.env["ir.sequence"].next_by_code("motel.booking") or "New"

    @api.depends("checkin_time", "checkout_time", "expected_checkout")
    def _compute_duration_hour(self):
        for rec in self:
            end_dt = rec.checkout_time or rec.expected_checkout
            if not rec.checkin_time or not end_dt:
                rec.duration_hour = 0.0
                continue
            delta = end_dt - rec.checkin_time
            rec.duration_hour = max(delta.total_seconds() / 3600.0, 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("booking_code", "New") == "New":
                vals["booking_code"] = self.env["ir.sequence"].next_by_code("motel.booking") or "New"
            if not vals.get("name"):
                vals["name"] = vals.get("booking_code") or "New"
        return super().create(vals_list)

    @api.constrains("checkin_time", "expected_checkout", "checkout_time")
    def _check_times(self):
        for rec in self:
            if rec.expected_checkout and rec.checkin_time and rec.expected_checkout <= rec.checkin_time:
                raise ValidationError("Expected checkout must be later than check-in.")
            if rec.checkout_time and rec.checkin_time and rec.checkout_time <= rec.checkin_time:
                raise ValidationError("Checkout time must be later than check-in.")

    @api.constrains("deposit_amount", "total_amount")
    def _check_amounts(self):
        for rec in self:
            if rec.deposit_amount and rec.deposit_amount < 0:
                raise ValidationError("Deposit amount must be non-negative.")
            if rec.total_amount and rec.total_amount < 0:
                raise ValidationError("Total amount must be non-negative.")

    @api.constrains("room_id", "checkin_time", "expected_checkout", "state")
    def _check_no_overlap(self):
        for rec in self:
            if not rec.room_id or not rec.checkin_time or not rec.expected_checkout:
                continue
            if rec.state not in constants.BOOKING_ACTIVE_STATES:
                continue
            domain = [
                ("id", "!=", rec.id),
                ("room_id", "=", rec.room_id.id),
                ("state", "in", list(constants.BOOKING_ACTIVE_STATES)),
                ("checkin_time", "<", rec.expected_checkout),
                ("expected_checkout", ">", rec.checkin_time),
            ]
            if self.search_count(domain):
                raise ValidationError("This room already has an overlapping active booking.")

    def _ensure_primary_guest(self):
        self.ensure_one()
        primary_count = len(self.guest_line_ids.filtered("is_primary"))
        if primary_count != 1:
            raise ValidationError("A booking must have exactly one primary guest.")

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                continue
            if not rec.expected_checkout:
                raise ValidationError("Expected checkout is required to confirm.")
            if not rec.room_price_hour_snapshot or not rec.room_price_night_snapshot:
                rec.room_price_hour_snapshot = rec.room_id.room_type_id.default_price_hour
                rec.room_price_night_snapshot = rec.room_id.room_type_id.default_price_night
            rec.state = "confirmed"
            rec.room_id.status = "reserved"

    def action_check_in(self):
        for rec in self:
            if rec.state not in ("confirmed",):
                raise ValidationError("Only confirmed bookings can be checked in.")
            primaries = rec.guest_line_ids.filtered("is_primary")
            if not primaries and len(rec.guest_line_ids) == 1:
                rec.guest_line_ids.is_primary = True
            rec._ensure_primary_guest()
            rec.state = "checked_in"
            rec.room_id.status = "occupied"
            rec.room_id.current_booking_id = rec.id

    def action_check_out(self):
        for rec in self:
            if rec.state != "checked_in":
                raise ValidationError("Only checked-in bookings can be checked out.")
            rec.checkout_time = fields.Datetime.now()
            rec.state = "checked_out"
            rec.room_id.status = "cleaning"
            rec.room_id.current_booking_id = False

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "confirmed"):
                raise ValidationError("Only draft/confirmed bookings can be cancelled.")
            rec.state = "cancelled"
            if rec.room_id.current_booking_id and rec.room_id.current_booking_id.id == rec.id:
                rec.room_id.current_booking_id = False
            if rec.room_id.status == "reserved":
                rec.room_id.status = "available"
