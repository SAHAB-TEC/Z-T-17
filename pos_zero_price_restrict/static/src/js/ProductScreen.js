/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
  async onClickPay() {

    const currentOrder = this.pos.get_order();
    currentOrder.orderlines.forEach(function (line) {
      const price = line.get_unit_display_price();
      if (price === 0) {
        // this.showPopup('ErrorPopup', {
        //   title: 'Zero Price not allowed',
        //   body: 'Only a positive price is allowed for confirming the order',
        // });
        return;
      }
    });
    super.onClickPay();
  },

  onNumpadClick(buttonValue) {
    if (buttonValue === "pay") {
      const currentOrder = this.pos.get_order();
      currentOrder.orderlines.forEach(function (line) {
        const price = line.get_unit_display_price();
        if (price === 0) {
          this.showPopup('ErrorPopup', {
            title: 'Zero Price not allowed',
            body: 'Only a positive price is allowed for confirming the order',
          });
          return;
        }
      });

      super.onNumpadClick(buttonValue);
    }
    else {
      super.onNumpadClick(buttonValue);
    }
  }
});
