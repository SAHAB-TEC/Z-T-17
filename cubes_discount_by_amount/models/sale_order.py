from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_by_amount = fields.Float(string='Discount (Amount)', default=0.0)


    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'discount_by_amount': self.discount_by_amount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.order_id.analytic_account_id:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'discount_by_amount','tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.discount_by_amount:
                discount_per_unit = line.discount_by_amount/line.product_uom_qty
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - discount_per_unit
                if line.price_unit != price:
                    line.price_unit = price
            tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
                line._convert_to_tax_base_line_dict()
            ])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })