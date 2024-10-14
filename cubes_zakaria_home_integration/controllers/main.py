# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from datetime import date, datetime, time
import logging
from odoo.http import request
from odoo import http, tools, SUPERUSER_ID
import json

_logger = logging.getLogger(__name__)


class ExternalApis(http.Controller):
    @http.route(['/api/example_product_obj'], type='json', auth="none", cors="*",
                csrf=False, website=True)
    def api_example_product_obj(self):
        product = request.env['product.product'].with_user(SUPERUSER_ID).search([], limit=1)
        if product:
            return product.read()
        return False

    @http.route(['/api/create_product'], type='json', auth="none", cors="*",
                csrf=False, website=True)
    def api_create_product(self, **post):
        product = request.env['product.template'].with_user(SUPERUSER_ID).create({
            'name': post.get('name'),
            'zakaria_id': post.get('id')
        })
        return {"status": 200, "data": product.read()}

    @http.route(['/api/create_customer'], type='json', auth="none", cors="*",
                csrf=False, website=True)
    def api_create_customer(self, **post):
        payload = post.get('payload').get('user')
        if not payload:
            return {"status": 404, "message": "Payload is invalid"}
        check_customer = request.env['res.partner'].with_user(SUPERUSER_ID).search([
            ('zakaria_id', '=', payload.get('id'))
        ])
        if check_customer:
            return {"status": 202, "message": "Customer is already exist"}
        customer = request.env['res.partner'].with_user(SUPERUSER_ID).create({
            'name': payload.get('first_name') + ' ' + payload.get('last_name'),
            'email': payload.get('email'),
            'zakaria_id': payload.get('id')
        })
        return {"status": 200, "data": customer.read()}

    @http.route(['/api/get_all_customers'], type='json', auth="none", cors="*",
                csrf=False, website=True)
    def api_get_all_customers(self):
        customers = request.env['res.partner'].with_user(SUPERUSER_ID).search([])
        return {"status": 200, "data": customers.read()}


class SaleOrderAPI(http.Controller):
    @http.route('/api/get_all_sale_orders', type='json', auth='none', methods=['GET'])
    def get_all_sale_orders(self, **kwargs):
        sale_orders = request.env['sale.order'].sudo().search([])
        sale_order_details = []
        for order in sale_orders:
            order_data = {
                'id': order.id,
                'name': order.name,
                'partner_id': order.partner_id.id,
                'date_order': order.date_order.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_term_id': order.payment_term_id.id,
                'amount_total': order.amount_total,
                'order_lines': [],
            }
            for line in order.order_line:
                line_data = {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'product_uom_id': line.product_uom.id,
                    'tax_id_id': line.tax_id.id,
                    'price_subtotal': line.price_subtotal,
                }
                order_data['order_lines'].append(line_data)
            sale_order_details.append(order_data)
        return {"status": 200, "data": json.loads(json.dumps(sale_order_details))}

    @http.route('/api/sale_order_details', type='json', auth='none', methods=['GET'])
    def get_sale_order_details(self, **kwargs):
        so_id = kwargs.get('id')
        sale_order = request.env['sale.order'].sudo().search([('id', '=', so_id)])
        if not sale_order:
            response_data = {'error': 'Sale order not found'}
            return {"data": json.loads(json.dumps(response_data))}
        order_data = {
            'name': sale_order.name,
            'partner_id': sale_order.partner_id.id,
            'date_order': sale_order.date_order.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_term_id': sale_order.payment_term_id.id,
            'amount_total': sale_order.amount_total,
            'order_lines': [],
        }
        for line in sale_order.order_line:
            line_data = {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'product_uom_id': line.product_uom.id,
                'tax_id_id': line.tax_id.id,
                'price_subtotal': line.price_subtotal,
            }
            order_data['order_lines'].append(line_data)
        return {"status": 200, "data": json.loads(json.dumps(order_data))}

    @http.route('/api/create_sale_order', type='json', auth="none", methods=['POST'], csrf=False)
    def create_sale_order(self, **post):
        payload_order = post.get('payload')
        customer_id = payload_order.get('customer_id')
        if customer_id:
            customer_id = request.env['res.partner'].sudo().search([
                ('zakaria_id', '=', payload_order.get('customer_id'))
            ], limit=1)
        else:
            customer_id = request.env.ref('cubes_zakaria_home_integration.zakaria_integration_partner')
            if payload_order.get('recipient_email'):
                check_email = request.env['res.partner'].sudo().search([
                    ('email', '=', payload_order.get('recipient_email'))
                ], limit=1)
                if check_email:
                    customer_id = check_email
        order = payload_order.get('order')
        if order and order.get('email'):
            check_email = request.env['res.partner'].sudo().search([
                ('email', '=', order.get('email'))
            ], limit=1)
            if check_email:
                customer_id = check_email
        state = post.get('notify_event')
        # partner_id = post.get('partner_id')
        # partner_id = request.env.ref('cubes_zakaria_home_integration.zakaria_integration_partner').id
        zakaria_so_id = order.get('id')
        currency = order.get('currency')
        # amount_tax = order.get('tax_amount')
        # amount_total = order.get('total_gross_amount')
        # amount_undiscounted = order.get('undiscounted_total_gross_amount')
        company_id = 1
        date_order = datetime.now()
        currency_record = request.env['res.currency'].sudo().search([('name', '=', currency)])
        check_so = request.env['sale.order'].sudo().search([
            ('zakaria_so_id', '=', zakaria_so_id),
        ])
        if not check_so:
            sale_order = request.env['sale.order'].sudo().create({
                'zakaria_so_id': zakaria_so_id,
                'Zakaria_state': state,
                'currency_id': currency_record.id if currency_record else None,
                # 'amount_tax': amount_tax,
                # 'amount_total': amount_total,
                # 'amount_undiscounted': amount_undiscounted,
                'partner_id': customer_id.id,
                'company_id': company_id,
                'date_order': date_order,
            })
            for line_data in order.get('lines'):
                product_id = line_data.get('product').get('id')
                product = request.env['product.product'].sudo().search([('zakaria_id', '=', product_id)], limit=1)
                if product.exists():
                    line_values = {
                        'order_id': sale_order.id,
                        'zakaria_so_line_id': line_data.get('id'),
                        'company_id': company_id,
                        'product_id': product.id,
                        'name': line_data.get('product_name'),
                        'product_uom_qty': line_data.get('quantity'),
                        'currency_id': request.env.company.currency_id.id,
                        'price_unit': float(line_data.get('unit_price_gross_amount')),
                        'discount': float(line_data.get('unit_discount_amount')),
                        'price_tax': float(line_data.get('total_tax_amount')),
                        # 'price_subtotal': float(line_data.get('total_gross_amount')),
                    }
                    print(line_values)
                    request.env['sale.order.line'].with_user(1).create(
                        line_values)  # check this sudo() not work " assert company, "convert amount from unknown company"
            return {'success': True, 'sale_order_id': sale_order.id}
        else:
            return {'success': False, 'message': 'The Sale order is exist'}

    @http.route('/api/update_sale_order', type='json', auth="none", methods=['PUT'], csrf=False)
    def update_sale_order(self, **post):
        payload_order = post.get('payload')
        state = post.get('notify_event')
        order_data = payload_order.get('order')
        # Extract the relevant fields from the order_data
        order_id = order_data.get('id')
        currency = order_data.get('currency')
        # total_gross_amount = order_data.get('total_gross_amount')
        # undiscounted_total_gross_amount = order_data.get('undiscounted_total_gross_amount')
        # tax_amount = order_data.get('tax_amount')
        lines = order_data.get('lines', [])

        order = request.env['sale.order'].sudo().search([('zakaria_so_id', '=', order_id)], limit=1)
        print(order)
        if order:
            currency_record = request.env['res.currency'].sudo().search([('name', '=', currency)])
            order.currency_id = currency_record.id if currency_record else None
            order.Zakaria_state = state
            # order.amount_total = total_gross_amount
            # order.untaxed_amount = undiscounted_total_gross_amount
            # order.amount_tax = tax_amount
            #
            # Update the order lines
            for line_data in lines:
                product_id = line_data.get('product', {}).get('id')
                product = request.env['product.product'].sudo().search([('zakaria_id', '=', product_id)], limit=1)
                product_name = line_data.get('product_name')
                quantity = line_data.get('quantity')
                unit_price_gross_amount = line_data.get('unit_price_gross_amount')
                # total_gross_amount_line = line_data.get('total_gross_amount')
                total_tax_amount_line = line_data.get('total_tax_amount')

                # Find the existing order line by product_id
                order_line = order.order_line.filtered(lambda line: line.product_id.id == product.id)
                if order_line:
                    # Update the existing order line
                    order_line.write({
                        'product_id': product.id,
                        'name': product_name,
                        'product_uom_qty': quantity,
                        'price_unit': unit_price_gross_amount,
                        'price_tax': total_tax_amount_line,
                        # 'price_total': total_gross_amount_line,
                    })
                else:
                    # Create a new order line if not found
                    order_line_data = {
                        'order_id': order.id,
                        'product_id': product.id,
                        'name': product_name,
                        'product_uom_qty': quantity,
                        'price_unit': unit_price_gross_amount,
                        'price_tax': total_tax_amount_line,
                        # 'price_total': total_gross_amount_line,
                    }
                    request.env['sale.order.line'].with_user(1).create(order_line_data)
            return {'success': True, 'message': 'Sale Order updated successfully'}


class AccountMoveAPI(http.Controller):
    @http.route('/api/get_all_invoices', type='json', auth='none', methods=['GET'])
    def get_all_invoices(self, **kwargs):
        account_moves = request.env['account.move'].sudo().search([('move_type', '=', 'out_invoice')])

        account_move_details = []

        for move in account_moves:
            move_data = {
                'id': move.id,
                'name': move.name,
                'partner_id': move.partner_id.id,
                'invoice_date': str(move.invoice_date),
                'payment_term_id': move.invoice_payment_term_id.id,
                'invoice_line_ids': [],
            }
            for line in move.invoice_line_ids:
                line_data = {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'account_id': line.account_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'product_uom_id': line.product_uom_id.id,
                    'tax_ids': line.tax_ids.ids,
                    'price_subtotal': line.price_subtotal,
                }
                move_data['invoice_line_ids'].append(line_data)
            account_move_details.append(move_data)
        return {"status": 200, "data": json.loads(json.dumps(account_move_details))}

    @http.route('/api/invoice_details', type='json', auth='none', methods=['GET'])
    def get_invoice_details(self, **kwargs):
        inv_id = kwargs.get('id')
        account_move = request.env['account.move'].sudo().search([('id', '=', inv_id)])
        print(account_move)
        if not account_move or account_move.move_type != 'out_invoice':
            response_data = {'error': 'Invoice not found'}
            return {"status": 200, "data": json.loads(json.dumps(response_data))}
        move_data = {
            'name': account_move.name,
            'partner_id': account_move.partner_id.id,
            'invoice_date': str(account_move.invoice_date),
            'payment_term_id': account_move.invoice_payment_term_id.id,
            'invoice_line_ids': [],
        }
        for line in account_move.invoice_line_ids:
            line_data = {
                'product_id': line.product_id.id,
                'name': line.name,
                'account_id': line.account_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'product_uom_id': line.product_uom_id.id,
                'tax_ids': line.tax_ids.ids,
                'price_subtotal': line.price_subtotal,
            }
            move_data['invoice_line_ids'].append(line_data)
        return {"status": 200, "data": json.loads(json.dumps(move_data))}

    @http.route('/api/create_invoice', type='json', auth="none", methods=['POST'], csrf=False)
    def create_invoice(self, **post):
        payload_order = post.get('payload')
        invoice = payload_order.get('invoice')
        state = post.get('notify_event')
        order_id = invoice.get('order_id')
        sale_order = request.env['sale.order'].with_user(1).search([('zakaria_so_id', '=', order_id)])
        print(sale_order)
        for order in sale_order:
            if order.state != 'sale':
                return {'success': False, 'Reason': "Please Confirm Sale Order %s" % order.name}
            else:
                if order.picking_ids:
                    transfer_state = order.picking_ids.mapped('state')
                    if 'done' not in transfer_state:
                        return {'success': False, 'Reason': "Please Validate Transfer of Sale Order %s" % order.name}
            move = order._create_invoices()
            move.zakaria_inv_id = invoice.get('id')
            move.Zakaria_state = state
        return {'success': True, 'account_move_id': move.id}

    @http.route('/api/update_invoice', type='json', auth="none", methods=['PUT'], csrf=False)
    def update_invoice(self, **post):
        payload_order = post.get('payload')
        invoice = payload_order.get('invoice')
        state = post.get('notify_event')
        inv_id = invoice.get('id')
        move = request.env['account.move'].sudo().search([('zakaria_inv_id', '=', inv_id)], limit=1)
        if move:
            move.Zakaria_state = state
            return {'success': True, 'message': 'Invoice updated successfully'}
        else:
            return {'success': False, 'message': 'Invoice not provided in data'}
