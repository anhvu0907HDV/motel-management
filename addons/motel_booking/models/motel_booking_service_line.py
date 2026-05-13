from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelBookingServiceLine(models.Model):
    _name = "motel.booking.service.line"
    _description = "Motel Booking Service Line"
    _order = "id desc"

    booking_id = fields.Many2one("motel.booking", required=True, ondelete="cascade", index=True)
    service_id = fields.Many2one("motel.service", required=True, ondelete="restrict", index=True)

    qty = fields.Float(default=1.0, required=True)
    unit_price = fields.Float(required=True)
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True)
    currency_id = fields.Many2one("res.currency", related="booking_id.currency_id", store=True, readonly=True)

    note = fields.Text()

    @api.depends("qty", "unit_price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.qty or 0.0) * (rec.unit_price or 0.0)

    @api.constrains("qty", "unit_price")
    def _check_qty_unit_price(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError("Service quantity must be greater than 0.")
            if rec.unit_price < 0:
                raise ValidationError("Unit price must be non-negative.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("service_id") and vals.get("unit_price") in (None, False):
                service = self.env["motel.service"].browse(vals["service_id"])
                vals["unit_price"] = service.price
        return super().create(vals_list)
