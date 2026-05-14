from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MotelGuest(models.Model):
    _name = "motel.guest"
    _description = "Motel Guest"
    _inherit = ["mail.thread", "mail.activity.mixin", "motel.active.mixin"]
    _rec_name = "full_name"

    _sql_constraints = [
        ("motel_guest_identity_number_uniq", "unique(identity_number)", "Identity number must be unique."),
    ]

    full_name = fields.Char(required=True, index=True, tracking=True)
    identity_number = fields.Char(index=True, tracking=True)
    dob = fields.Date(tracking=True)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        tracking=True,
    )
    nationality = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    address = fields.Text(tracking=True)

    issue_date = fields.Date(tracking=True)
    issue_place = fields.Char(tracking=True)

    portrait = fields.Binary(
        attachment=True,
        groups="motel_security.group_motel_admin,motel_security.group_motel_receptionist",
    )
    cccd_front = fields.Binary(
        attachment=True,
        groups="motel_security.group_motel_admin,motel_security.group_motel_receptionist",
    )
    cccd_back = fields.Binary(
        attachment=True,
        groups="motel_security.group_motel_admin,motel_security.group_motel_receptionist",
    )

    ocr_text = fields.Text(
        groups="motel_security.group_motel_admin,motel_security.group_motel_receptionist",
    )
    ocr_verified = fields.Boolean(default=False, tracking=True)
    ocr_confidence = fields.Float(digits=(16, 4))

    is_blacklisted = fields.Boolean(default=False, tracking=True)
    blacklist_reason = fields.Text()

    def name_get(self):
        res = []
        for rec in self:
            name = (rec.full_name or "").strip()
            if not name:
                name = f"Guest {rec.id}"
            if rec.identity_number:
                name = f"{name} ({rec.identity_number})"
            res.append((rec.id, name))
        return res

    @api.constrains("identity_number")
    def _check_identity_number(self):
        for rec in self:
            if rec.identity_number and " " in rec.identity_number:
                raise ValidationError("Identity number must not contain spaces.")
