from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    qr_bank_image = fields.Binary(string="Bank QR", attachment=True)
    qr_momo_image = fields.Binary(string="MoMo QR", attachment=True)
    qr_vnpay_image = fields.Binary(string="VNPay QR", attachment=True)

