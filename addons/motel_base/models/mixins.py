from odoo import api, fields, models


class MotelCodeMixin(models.AbstractModel):
    _name = "motel.code.mixin"
    _description = "Motel Code Mixin"

    code = fields.Char(index=True, copy=False)

    @api.model
    def _motel_sequence_code(self) -> str:
        return ""

    def _motel_next_code(self) -> str:
        sequence_code = self._motel_sequence_code()
        if not sequence_code:
            return ""
        return self.env["ir.sequence"].next_by_code(sequence_code) or ""

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                next_code = self._motel_next_code()
                if next_code:
                    vals["code"] = next_code
        return super().create(vals_list)


class MotelActiveMixin(models.AbstractModel):
    _name = "motel.active.mixin"
    _description = "Motel Active Mixin"

    active = fields.Boolean(default=True, index=True)
