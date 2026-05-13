from odoo import api, fields, models


class MotelDashboard(models.Model):
    _name = "motel.report.dashboard"
    _description = "Motel Dashboard"

    name = fields.Char(default="Dashboard", required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    total_rooms = fields.Integer(compute="_compute_kpis")
    occupied_rooms = fields.Integer(compute="_compute_kpis")
    available_rooms = fields.Integer(compute="_compute_kpis")
    occupancy_rate = fields.Float(compute="_compute_kpis", digits=(16, 2))
    daily_revenue = fields.Monetary(compute="_compute_kpis", currency_field="currency_id")

    @api.depends_context("uid")
    def _compute_kpis(self):
        today = fields.Date.context_today(self)
        Room = self.env["motel.room"].sudo()
        Booking = self.env["motel.booking"].sudo()

        total_rooms = Room.search_count([("active", "=", True)])
        occupied_rooms = Room.search_count([("active", "=", True), ("status", "=", "occupied")])
        available_rooms = Room.search_count([("active", "=", True), ("status", "=", "available")])

        bookings = Booking.search([("state", "=", "checked_out"), ("checkout_time", "!=", False)])
        daily_revenue = sum(
            b.total_amount
            for b in bookings
            if b.checkout_time and fields.Date.to_date(b.checkout_time) == today
        )

        for rec in self:
            rec.total_rooms = total_rooms
            rec.occupied_rooms = occupied_rooms
            rec.available_rooms = available_rooms
            rec.occupancy_rate = (occupied_rooms / total_rooms * 100.0) if total_rooms else 0.0
            rec.daily_revenue = daily_revenue
