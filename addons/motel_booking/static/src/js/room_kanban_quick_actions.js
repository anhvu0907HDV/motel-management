/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ViewButton } from "@web/views/view_button/view_button";

patch(ViewButton.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.notification = useService("notification");
    },

    async onClick(ev) {
        const clickParams = this.clickParams || {};
        const record = this.props.record;

        const isRoomQuickAction =
            record?.resModel === "motel.room" &&
            record?.resId &&
            clickParams.type === "object" &&
            [
                "action_quick_set_available",
                "action_quick_set_cleaning",
                "action_quick_set_maintenance",
                "action_cycle_status",
            ].includes(
                clickParams.name
            );

        if (!isRoomQuickAction) {
            return super.onClick(ev);
        }

        ev.preventDefault();

        const statusByMethod = {
            action_quick_set_available: "available",
            action_quick_set_cleaning: "cleaning",
            action_quick_set_maintenance: "maintenance",
        };
        let newStatus = statusByMethod[clickParams.name];

        try {
            const result = await this.orm.call("motel.room", clickParams.name, [[record.resId]], {});
            if (clickParams.name === "action_cycle_status" && typeof result === "string") {
                newStatus = result;
            }
            if (newStatus) {
                await record.update({ status: newStatus }, { save: false });
            }
            this.notification.add(_t("Room status updated."), { type: "success" });
        } catch (e) {
            this.notification.add(_t("Could not update room status."), { type: "danger" });
            throw e;
        }
    },
});
