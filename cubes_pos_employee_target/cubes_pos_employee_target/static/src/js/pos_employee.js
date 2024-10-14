/** @odoo-module */
import { PosGlobalState} from 'point_of_sale.models';
import Registries from 'point_of_sale.Registries';

// Store the employee selected
var { Order } = require('point_of_sale.models');
const L10nInOrder = (Order) => class L10nInOrder extends Order {
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.pos_employee_id = json.pos_employee_id;
    }
    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        json.pos_employee_id = this.pos_employee_id;
        return json;
    }
};
Registries.Model.extend(Order, L10nInOrder);

// Load customer model in odoo 16
const NewPosGlobalState = (PosGlobalState) => class NewPosGlobalState extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.hr_employee = loadedData['hr.employee'];
    }
}
Registries.Model.extend(PosGlobalState, NewPosGlobalState);

// Custom POP Screen
odoo.define('cubes_pos_employee_target.EmployeePosScreen', function (require) {
    'use strict';
    const { Gui } = require('point_of_sale.Gui');
    const { useListener } = require("@web/core/utils/hooks");
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');
    const rpc = require('web.rpc');
    const { parse } = require('web.field_utils');
    const { useRef, useState } = owl;

    class EmployeePosScreen extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            useListener('click-employee', this.EmployeePosScreen);
        }
        confirm(){
            this.env.pos.get_order().pos_employee_id = $('#select_employee option:selected').val();
            this.env.pos.get_order().pos_employee_name = $('#select_employee option:selected').text();
            this.env.posbus.trigger('close-popup', {
                popupId: this.props.id,
                response: { confirmed: true, payload: null },
            });
        }

        EmployeePosScreen(item) {
            this.env.posbus.trigger('close-popup', {
                popupId: this.props.id,
                response: { confirmed: true, payload: null },
            });
        }
    }

    // Create EmployeePosScreen popup
    EmployeePosScreen.template = 'EmployeePosScreen';
    EmployeePosScreen.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Select Employee',
        body: '',
    };

    Registries.Component.add(EmployeePosScreen);

    return EmployeePosScreen;
});

// Custom Actionpad Button
odoo.define('pos_button.PosEmployeeSelect', function(require) {
'use strict';
  const { Gui } = require('point_of_sale.Gui');
  const PosComponent = require('point_of_sale.PosComponent');
  const { identifyError } = require('point_of_sale.utils');
  const ProductScreen = require('point_of_sale.ProductScreen');
  const { useListener } = require("@web/core/utils/hooks");
  const Registries = require('point_of_sale.Registries');
  const PaymentScreen = require('point_of_sale.PaymentScreen');


  class PosEmployeeSelect extends PosComponent {
      setup() {
          super.setup();
          useListener('click', this.onClick);
      }
     async onClick() {
       const { confirmed} = await
              this.showPopup("EmployeePosScreen", {
              title: this.env._t('Select Employee'),
              pos_employee: this.env.pos.hr_employee
        });
    }
  }
PosEmployeeSelect.template = 'PosEmployeeSelect';
  ProductScreen.addControlButton({
      component: PosEmployeeSelect,
      condition: function() {
          return this.env.pos;
      },
  });
  Registries.Component.add(PosEmployeeSelect);
  return PosEmployeeSelect;
});
