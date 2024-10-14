odoo.define('cubes_pos_employee_target.EmployeePosScreen', function (require) {
    'use strict';
    const { Gui } = require('point_of_sale.Gui');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');
    const rpc = require('web.rpc');
    const { parse } = require('web.field_utils');
    const { useState, useRef, useContext, useExternalListener } = owl.hooks;
    const { useListener } = require('web.custom_hooks');


    /** @odoo-module */
    var models = require('point_of_sale.models');
    var _super_pos_model = models.PosModel.prototype;
    var _models = models.PosModel.prototype.models;
    models.load_fields("pos.order", "pos_employee_id");
    models.load_fields("hr.employee", "id");

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.pos_employee_id = false;
        },
        export_for_printing: function () {
            var result = _super_order.export_for_printing.apply(this, arguments);
            result['pos_employee_id'] = this.pos_employee_id;
            return result;
        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.bind(this)();
            json.pos_employee_id = this.pos_employee_id;
            return json;
        },
        set_pos_employee_id: function(value){
            this.pos_employee_id = value;
        },
        get_pos_employee_id: function(value) {
            return this.pos_employee_id;
        },
    });

    class EmployeePosScreen extends AbstractAwaitablePopup {
        setup() {
            super.setup();
        }
        constructor() {
            super(...arguments);
            useListener('click-employee', this.EmployeePosScreen);
        }
        confirm(){
            this.env.pos.get_order().pos_employee_id = $('#select_employee option:selected').val();
            this.env.pos.get_order().set_pos_employee_id($('#select_employee option:selected').val());
            this.env.pos.get_order().pos_employee_name = $('#select_employee option:selected').text();
            this.trigger('close-popup');
        }

        EmployeePosScreen(item) {
            this.trigger('close-popup');
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
        var self = this;
        var records = self.rpc({
            model: 'hr.employee',
            method: 'search_read',
            args: [],
        });
        return records.then(async function (employee_data) {
           const { confirmed} = await
                  self.showPopup("EmployeePosScreen", {
                  title: self.env._t('Select Employee'),
                  pos_employee: employee_data
            });
        })
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
