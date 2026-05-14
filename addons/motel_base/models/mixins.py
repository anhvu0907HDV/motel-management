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


class MotelNotificationMixin(models.AbstractModel):
    _name = "motel.notification.mixin"
    _description = "Motel Notification Mixin"

    def _motel_display_notification(
        self,
        *,
        title: str,
        message: str,
        notif_type: str = "success",
        sticky: bool = False,
        reload: bool = True,
    ):
        params = {
            "title": title,
            "message": message,
            "type": notif_type,
            "sticky": sticky,
        }
        if reload:
            params["next"] = {"type": "ir.actions.client", "tag": "reload"}
        return {"type": "ir.actions.client", "tag": "display_notification", "params": params}
