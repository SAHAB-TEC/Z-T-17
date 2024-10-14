/** @odoo-module */

import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(Order.prototype, {
    //@Override this.get_orderlines()
    pay() {

        var is_zero = false;
        this.get_orderlines().forEach(function (line) {
            const price = line.get_unit_display_price();
            if (price === 0) {
                is_zero = true;
                return;
            }
        });
        if (is_zero) {
            this.env.services.popup.add(ErrorPopup, {
                title: _t("Error"),
                body: _t("Zero Price not allowed. Only a positive price is allowed for confirming the order."),
            });
            return false;
        }
        return super.pay(...arguments);
    },
});
