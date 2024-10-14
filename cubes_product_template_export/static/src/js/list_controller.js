/** @odoo-module */
/**
 * This file will used to hide the selected options from the list view
 */
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

//import session from 'web.session';
// var session = require('web.session');
patch(ListController.prototype, 'cubes_product_template_export/static/src/js/list_controller.js.ListController', {
/**
* This function will used to hide the selected options from the list view
*/
    async willStart() {
        var self = this;
        var model = self.modelName;
        if (model  == 'product.template')
        {
            // session.user_has_group('cubes_product_template_export.export_product_group').then(function (hasGroup)
            // {
            hasGroups = self.user_has_groups('cubes_product_template_export.export_product_group')
            if (hasGroup)
            {
                self.isExportEnable = true;
            }
            else
            {
                self.isExportEnable = false;
            }
            // });
        }
    },
});
