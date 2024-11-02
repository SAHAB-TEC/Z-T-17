# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import html_escape, is_html_empty

from odoo.addons.account.models.account_move_line import AccountMoveLine as OriginalAccountMoveLine


#forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')

def write(self, vals):
    # OVERRIDE
    ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
    BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids','discount_by_amount')
    PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tax_tag_ids']
    PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency',
                                                                   'currency_id', 'partner_id']
    PROTECTED_FIELDS_RECONCILIATION = ('account_id', 'date', 'debit', 'credit', 'amount_currency', 'currency_id')

    account_to_write = self.env['account.account'].browse(vals['account_id']) if 'account_id' in vals else None

    # Check writing a deprecated account.
    if account_to_write and account_to_write.deprecated:
        raise UserError(_('You cannot use a deprecated account.'))

    for line in self:
        if line.parent_state == 'posted':
            if line.move_id.restrict_mode_hash_table and set(vals).intersection(INTEGRITY_HASH_LINE_FIELDS):
                raise UserError(_(
                    "You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(
                    INTEGRITY_HASH_LINE_FIELDS))
            if any(key in vals for key in ('tax_ids', 'tax_line_id')):
                raise UserError(_(
                    'You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so.'))

        # Check the lock date.
        if line.parent_state == 'posted' and any(
                self.env['account.move']._field_will_change(line, vals, field_name) for field_name in
                PROTECTED_FIELDS_LOCK_DATE):
            line.move_id._check_fiscalyear_lock_date()

        # Check the tax lock date.
        if line.parent_state == 'posted' and any(
                self.env['account.move']._field_will_change(line, vals, field_name) for field_name in
                PROTECTED_FIELDS_TAX_LOCK_DATE):
            line._check_tax_lock_date()

        # Check the reconciliation.
        if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in
               PROTECTED_FIELDS_RECONCILIATION):
            line._check_reconciliation()

        # Check switching receivable / payable accounts.
        if account_to_write:
            account_type = line.account_id.user_type_id.type
            if line.move_id.is_sale_document(include_receipts=True):
                if (account_type == 'receivable' and account_to_write.user_type_id.type != account_type) \
                        or (account_type != 'receivable' and account_to_write.user_type_id.type == 'receivable'):
                    raise UserError(_(
                        "You can only set an account having the receivable type on payment terms lines for customer invoice."))
            if line.move_id.is_purchase_document(include_receipts=True):
                if (account_type == 'payable' and account_to_write.user_type_id.type != account_type) \
                        or (account_type != 'payable' and account_to_write.user_type_id.type == 'payable'):
                    raise UserError(_(
                        "You can only set an account having the payable type on payment terms lines for vendor bill."))

    # Tracking stuff can be skipped for perfs using tracking_disable context key
    if not self.env.context.get('tracking_disable', False):
        # Get all tracked fields (without related fields because these fields must be manage on their own model)
        tracking_fields = []
        for value in vals:
            field = self._fields[value]
            if hasattr(field, 'related') and field.related:
                continue  # We don't want to track related field.
            if hasattr(field, 'tracking') and field.tracking:
                tracking_fields.append(value)
        ref_fields = self.env['account.move.line'].fields_get(tracking_fields)

        # Get initial values for each line
        move_initial_values = {}
        for line in self.filtered(lambda l: l.move_id.posted_before):  # Only lines with posted once move.
            for field in tracking_fields:
                # Group initial values by move_id
                if line.move_id.id not in move_initial_values:
                    move_initial_values[line.move_id.id] = {}
                move_initial_values[line.move_id.id].update({field: line[field]})

    result = True
    for line in self:
        cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
        if not cleaned_vals:
            continue

        # Auto-fill amount_currency if working in single-currency.
        if 'currency_id' not in cleaned_vals \
                and line.currency_id == line.company_currency_id \
                and any(field_name in cleaned_vals for field_name in ('debit', 'credit')):
            cleaned_vals.update({
                'amount_currency': vals.get('debit', 0.0) - vals.get('credit', 0.0),
            })
        result |= super(OriginalAccountMoveLine, line).write(cleaned_vals)

        if not line.move_id.is_invoice(include_receipts=True):
            continue

        # Ensure consistency between accounting & business fields.
        # As we can't express such synchronization as computed fields without cycling, we need to do it both
        # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
        # business [resp. accounting] fields are recomputed.
        if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
            price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
            to_write = line._get_fields_onchange_balance(price_subtotal=price_subtotal)
            to_write.update(line._get_price_total_and_subtotal(
                price_unit=to_write.get('price_unit', line.price_unit),
                quantity=to_write.get('quantity', line.quantity),
                discount=to_write.get('discount', line.discount),
                discount_by_amount=to_write.get('discount_by_amount', line.discount_by_amount),
            ))
            result |= super(OriginalAccountMoveLine, line).write(to_write)
        elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
            to_write = line._get_price_total_and_subtotal()
            to_write.update(line._get_fields_onchange_subtotal(
                price_subtotal=to_write['price_subtotal'],
            ))
            result |= super(OriginalAccountMoveLine, line).write(to_write)

    # Check total_debit == total_credit in the related moves.
    if self._context.get('check_move_validity', True):
        container = {'records': self}
        self.mapped('move_id')._check_balanced(container)

    self.mapped('move_id')._synchronize_business_models({'line_ids'})

    if not self.env.context.get('tracking_disable', False):
        # Log changes to move lines on each move
        for move_id, modified_lines in move_initial_values.items():
            for line in self.filtered(lambda l: l.move_id.id == move_id):
                tracking_value_ids = line._mail_track(ref_fields, modified_lines)[1]
                if tracking_value_ids:
                    msg = f"{html_escape(_('Journal Item'))} <a href=# data-oe-model=account.move.line data-oe-id={line.id}>#{line.id}</a> {html_escape(_('updated'))}"
                    line.move_id._message_log(
                        body=msg,
                        tracking_value_ids=tracking_value_ids
                    )

    return result


@api.model_create_multi
def create(self, vals_list):
    # OVERRIDE
    ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
    BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids','discount_by_amount')

    for vals in vals_list:
        move = self.env['account.move'].browse(vals['move_id'])
        vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message
        # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
        # company.
        currency_id = vals.get('currency_id') or move.company_id.currency_id.id
        if currency_id == move.company_id.currency_id.id:
            balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
            vals.update({
                'currency_id': currency_id,
                'amount_currency': balance,
            })
        else:
            vals['amount_currency'] = vals.get('amount_currency', 0.0)
        if move.is_invoice(include_receipts=True):
            currency = move.currency_id
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
            tax_ids = set(taxes.ids)
            taxes = self.env['account.tax'].browse(tax_ids)
            # Ensure consistency between accounting & business fields.
            # As we can't express such synchronization as computed fields without cycling, we need to do it both
            # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
            # business [resp. accounting] fields are recomputed.
            if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                price_subtotal = self._get_price_total_and_subtotal_model(
                    vals.get('price_unit', 0.0),
                    vals.get('quantity', 0.0),
                    vals.get('discount', 0.0),
                    currency,
                    self.env['product.product'].browse(vals.get('product_id')),
                    partner,
                    taxes,
                    move.move_type,
                    vals.get('discount_by_amount', 0.0),
                ).get('price_subtotal', 0.0)
                vals.update(self._get_fields_onchange_balance_model(
                    vals.get('quantity', 0.0),
                    vals.get('discount', 0.0),
                    vals['amount_currency'],
                    move.move_type,
                    currency,
                    taxes,
                    price_subtotal,
                    vals.get('discount_by_amount', 0.0),
                ))
                vals.update(self._get_price_total_and_subtotal_model(
                    vals.get('price_unit', 0.0),
                    vals.get('quantity', 0.0),
                    vals.get('discount', 0.0),
                    currency,
                    self.env['product.product'].browse(vals.get('product_id')),
                    partner,
                    taxes,
                    move.move_type,
                    vals.get('discount_by_amount', 0.0),
                ))
            elif any(vals.get(field) for field in BUSINESS_FIELDS):
                vals.update(self._get_price_total_and_subtotal_model(
                    vals.get('price_unit', 0.0),
                    vals.get('quantity', 0.0),
                    vals.get('discount', 0.0),
                    currency,
                    self.env['product.product'].browse(vals.get('product_id')),
                    partner,
                    taxes,
                    move.move_type,
                    vals.get('discount_by_amount', 0.0),
                ))
                vals.update(self._get_fields_onchange_subtotal_model(
                    vals['price_subtotal'],
                    move.move_type,
                    currency,
                    move.company_id,
                    move.date,
                ))

    lines = super(OriginalAccountMoveLine, self).create(vals_list)
    moves = lines.mapped('move_id')
    if self._context.get('check_move_validity', True):
        container = {'records': self}
        moves._check_balanced(container)
    moves.filtered(lambda m: m.state == 'posted')._check_fiscalyear_lock_date()
    lines.filtered(lambda l: l.parent_state == 'posted')._check_tax_lock_date()
    moves._synchronize_business_models({'line_ids'})
    return lines

OriginalAccountMoveLine.create = create
OriginalAccountMoveLine.write = write



class AccountMoveLineEdited(models.Model):
    _inherit = "account.move.line"

    discount_by_amount = fields.Float(string='Discount (Amount)', default=0.0)

    @api.onchange('quantity', 'discount','discount_by_amount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_price_total_and_subtotal())
            line.update(line._get_fields_onchange_subtotal())

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None, discount_by_amount=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=self.price_unit if price_unit is None else price_unit,
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            currency=self.currency_id if currency is None else currency,
            product=self.product_id if product is None else product,
            partner=self.partner_id if partner is None else partner,
            taxes=self.tax_ids if taxes is None else taxes,
            move_type=self.move_id.move_type if move_type is None else move_type,
            discount_by_amount=self.discount_by_amount if discount_by_amount is None else discount_by_amount,
        )

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type, discount_by_amount):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.

        #line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        #subtotal = quantity * line_discount_price_unit
        #### Custom start
        if discount_by_amount:
            discount_per_unit = discount_by_amount / quantity
            line_discount_price_unit = price_unit * (1 - (discount / 100.0)) - discount_per_unit
            subtotal = quantity * line_discount_price_unit
        else:
            line_discount_price_unit = price_unit * (1 - (discount / 100.0))
            subtotal = quantity * line_discount_price_unit

        #### Custom end

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                                                                             quantity=quantity, currency=currency,
                                                                             product=product, partner=partner,
                                                                             is_refund=move_type in (
                                                                             'out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res


    def _get_fields_onchange_balance(self, quantity=None, discount=None, amount_currency=None, move_type=None, currency=None, taxes=None, price_subtotal=None, force_computation=False,discount_by_amount=None):
        self.ensure_one()
        return self._get_fields_onchange_balance_model(
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            amount_currency=self.amount_currency if amount_currency is None else amount_currency,
            move_type=self.move_id.move_type if move_type is None else move_type,
            currency=(self.currency_id or self.move_id.currency_id) if currency is None else currency,
            taxes=self.tax_ids if taxes is None else taxes,
            price_subtotal=self.price_subtotal if price_subtotal is None else price_subtotal,
            force_computation=force_computation,
            discount_by_amount=self.discount_by_amount if discount_by_amount is None else discount_by_amount,
        )

    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, amount_currency, move_type, currency, taxes, price_subtotal, discount_by_amount,force_computation=False ):
        ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
        in some accounting fields such as 'balance'.

        This method is a bit complex as we need to handle some special cases.
        For example, setting a positive balance with a 100% discount.

        :param quantity:        The current quantity.
        :param discount:        The current discount.
        :param amount_currency: The new balance in line's currency.
        :param move_type:       The type of the move.
        :param currency:        The currency.
        :param taxes:           The applied taxes.
        :param price_subtotal:  The price_subtotal.
        :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        amount_currency *= sign

        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if not force_computation and currency.is_zero(amount_currency - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency, currency=currency, handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    amount_currency += tax_res['amount']

        discount_factor = 1 - (discount / 100.0)
        if amount_currency and discount_factor:
            # discount != 100%
            vals = {
                'discount_by_amount':discount_by_amount,
                'quantity': quantity or 1.0,
                'price_unit': amount_currency / discount_factor / (quantity or 1.0),
            }
        elif amount_currency and not discount_factor:
            # discount == 100%
            vals = {
                'discount_by_amount': discount_by_amount,
                'quantity': quantity or 1.0,
                'discount': 0.0,
                'price_unit': amount_currency / (quantity or 1.0),
            }
        elif not discount_factor:
            # balance of line is 0, but discount  == 100% so we display the normal unit_price
            vals = {'discount_by_amount':discount_by_amount,}
        else:
            # balance is 0, so unit price is 0 as well
            vals = {'price_unit': 0.0,
                    'discount_by_amount':discount_by_amount,}
        return vals
