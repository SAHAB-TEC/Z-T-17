# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # real_warehouse_id = fields.Many2one('stock.warehouse')

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Source Warehouse",
        readonly=False,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="If a source warehouse is selected, "
        "it will be used to define the route. "
        "Otherwise, it will get the warehouse of "
        "the sale order",
        store=True,
        related=False,
        compute_sudo=False,
    )

    # @api.onchange("warehouse_id")
    # def _depend_wharehouse(self):
    #     for rec in self:
    #         rec.real_warehouse_id = rec.warehouse_id.id

    def _compute_qty_at_date(self):
        """
        Inherit the compute (in sale_stock module) to keep the warehouse_id
        set on the line.
        @return:order_id.
        """
        save_wh = {rec: rec.warehouse_id for rec in self}
        result = super()._compute_qty_at_date()
        # for rec in self:
        #     rec.warehouse_id = save_wh.get(rec, False)
        return result

    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be
        created from a stock rule comming from a sale order line.
        This method could be override in order to add other custom key that
        could be used in move/po creation.
        """
        values = super()._prepare_procurement_values(group_id)
        self.ensure_one()
        # if self.warehouse_id:
        #     values["warehouse_id"] = self.warehouse_id
        return values

    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        priority = 10
        key = super()._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        warehouse = self.warehouse_id or self.order_id.warehouse_id
        return priority, warehouse.id

