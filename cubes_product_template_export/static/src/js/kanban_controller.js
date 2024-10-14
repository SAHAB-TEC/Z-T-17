/** @odoo-module */
/**
 * This file will used to hide the selected options from the kanban view
 */
import { KanbanController } from "@web/views/kanban/kanban_controller";
// import session from 'web.session';
import { patch } from "@web/core/utils/patch";

patch(KanbanController.prototype, 'cubes_product_template_export/static/src/js/kanban_controller.js.KanbanController', {
/**
* This function will used to hide the selected options from the kanban view
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
