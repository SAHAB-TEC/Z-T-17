import logging
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import SQL

_logger = logging.getLogger(__name__)

class AccountBankReconciliationReportHandler(models.AbstractModel):
    _inherit = 'account.bank.reconciliation.report.handler'

    def _bank_reconciliation_report_custom_engine_common(self, options, internal_type, current_groupby, from_last_statement, unreconciled=True):
        """
            Retrieve entries for bank reconciliation based on specified parameters.
            Parameters:
            - options (dict): A dictionary containing options of the report.
            - internal_type (str): The internal type used for classification (e.g., receipt, payment). For the receipt
                                   we will query the entries with a positive amounts and for the payment
                                   the negative amounts.
                                   If the internal type is another thing that receipt or payment it will get all the
                                   entries position or negative
            - current_groupby (str): The current grouping criteria.
            - last_statement (bool, optional): If True, query entries from the last bank statement.
                                               Otherwise, query entries that are not part of the last bank
                                               statement.
            - unreconciled (bool, optional): If True, query the unreconciled entries only

        """
        journal, journal_currency, _company_currency = self._get_bank_journal_and_currencies(options)
        if not journal:
            return self._build_custom_engine_result()

        report = self.env['account.report'].browse(options['report_id'])
        report._check_groupby_fields([current_groupby] if current_groupby else [])

        def build_result_dict(query_res_lines):
            if current_groupby == 'id':
                res = query_res_lines[0]
                reconcile_rate = 0
                if not journal_currency.is_zero(res['suspense_balance']):
                    reconcile_rate = abs(res['suspense_balance']) / (abs(res['suspense_balance']) + abs(res['other_balance']))
                foreign_currency = self.env['res.currency'].browse(res['foreign_currency_id'])

                return self._build_custom_engine_result(
                    date=res['date'] if res['date'] else None,
                    label=res['payment_ref'] or res['ref'] or '/',
                    amount_currency=res['amount_currency'] * reconcile_rate if res['amount_currency'] else None,
                    amount_currency_currency_id=foreign_currency.id if res['foreign_currency_id'] else None,
                    currency=foreign_currency.display_name if res['foreign_currency_id'] else None,
                    amount=res['amount'] * reconcile_rate if res['amount'] else None,
                    amount_currency_id=journal_currency.id,
                )
            else:
                amount = 0
                for res in query_res_lines:
                    if not journal_currency.is_zero(res['suspense_balance']) and not journal_currency.is_zero(res['other_balance']):
                        reconcile_rate = abs(res['suspense_balance']) / (abs(res['suspense_balance']) + abs(res['other_balance']))
                        amount += res.get('amount', 0) * reconcile_rate if unreconciled else res.get('amount', 0)

                return self._build_custom_engine_result(
                    amount=amount,
                    amount_currency_id=journal_currency.id,
                    has_sublines=bool(len(query_res_lines)),
                )

        tables, where_clause, where_params = report._query_get(options, 'strict_range', domain=[
            ('journal_id', '=', journal.id),
            ('account_id', '!=', journal.default_account_id.id),
        ])

        if from_last_statement:
            last_statement_id = self._get_last_bank_statement(journal, options).id
            if last_statement_id:
                last_statement_id_condition = SQL("st_line.statement_id = %s", last_statement_id)
            else:
                # If there is no last statement, the last statement section must be empty and the other must have all
                # transaction
                return self._compute_result([], current_groupby, build_result_dict)
        else:
            last_statement_id_condition = SQL("st_line.statement_id IS NULL")

        if internal_type == 'receipts':
            st_line_amount_condition = SQL("AND st_line.amount > 0")
        elif internal_type == 'payments':
            st_line_amount_condition = SQL("AND st_line.amount < 0")
        else:
            # For the Transaction without statement, the internal type is 'all'
            st_line_amount_condition = SQL("")

        # Build query
        query = SQL(
            """
           SELECT %(select_from_groupby)s,
                  st_line.id,
                  move.name,
                  move.ref,
                  move.date,
                  st_line.payment_ref,
                  st_line.amount,
                  st_line.amount_currency,
                  st_line.foreign_currency_id,
                  COALESCE(SUM(CASE WHEN account_move_line.account_id = %(suspens_journal_1)s THEN account_move_line.balance ELSE 0.0 END), 0.0) AS suspense_balance,
                  COALESCE(SUM(CASE WHEN account_move_line.account_id = %(suspens_journal_2)s THEN 0.0 ELSE account_move_line.balance END), 0.0) AS other_balance
             FROM %(tables)s
             JOIN account_bank_statement_line st_line ON st_line.move_id = account_move_line.move_id
             JOIN account_move move ON move.id = st_line.move_id
            WHERE %(where_clause)s
                  %(is_unreconciled)s
                  %(st_line_amount_condition)s
              AND %(last_statement_id_condition)s
         GROUP BY %(group_by)s,
                  st_line.id,
                  move.id
            """,
            select_from_groupby=SQL("%s AS grouping_key", SQL.identifier('account_move_line', current_groupby)) if current_groupby else SQL('null'),
            suspens_journal_1=journal.suspense_account_id.id,
            suspens_journal_2=journal.suspense_account_id.id,
            tables=SQL(tables),
            where_clause=SQL(where_clause, *where_params),
            is_unreconciled=SQL("AND NOT st_line.is_reconciled") if unreconciled else SQL(""),
            st_line_amount_condition=st_line_amount_condition,
            last_statement_id_condition=last_statement_id_condition,
            group_by=SQL.identifier('account_move_line', current_groupby) if current_groupby else SQL('st_line.id'),  # Same key in the groupby because we can't put a null key in a group by
        )

        self._cr.execute(query)
        query_res_lines = self._cr.dictfetchall()

        return self._compute_result(query_res_lines, current_groupby, build_result_dict)


