/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { KanbanRecord } from "@web/views/kanban/kanban_record";

patch(KanbanRecord.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.notification = useService("notification");
    },

    async motelQuickSetStatus(newStatus) {
        const record = this.props.record;
        if (!record || record.resModel !== "motel.room" || !record.resId) {
            return;
        }

        const methodByStatus = {
            available: "action_quick_set_available",
            cleaning: "action_quick_set_cleaning",
            maintenance: "action_quick_set_maintenance",
        };
        const method = methodByStatus[newStatus];
        if (!method) {
            return;
        }

        try {
            await this.orm.call("motel.room", method, [[record.resId]], {});
            await record.update({ status: newStatus }, { save: false });
            this.notification.add(_t("Room status updated."), { type: "success" });
        } catch (e) {
            this.notification.add(_t("Could not update room status."), { type: "danger" });
            throw e;
        }
    },
});
