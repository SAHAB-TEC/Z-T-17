/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {

    setup() {
        super.setup(...arguments);
    },
    

    export_for_printing() {
        return {
            ...super.export_for_printing(...arguments),
            client: this.partner,
            headerData : {
                ...this.pos.getReceiptHeaderData(this),
                client: this.partner,
            }
        };
    },


    // export_for_printing() {
    //     const result = super.export_for_printing(...arguments);

    //     result.client = this.partner;

    //     result.headerData = {
    //         ...this.pos.getReceiptHeaderData(this),
    //         client: this.partner,
    //     }
    //     return result;
    // },
});
