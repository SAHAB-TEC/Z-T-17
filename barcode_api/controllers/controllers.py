# -*- coding: utf-8 -*-
import json
import odoo
import requests
import threading
import werkzeug.exceptions
import werkzeug.serving
import werkzeug.wrappers
from odoo import http, models, fields
from odoo.http import request, Response
# , JsonRPCDispatcher)
from odoo.service import wsgi_server
from odoo.tools import date_utils
from odoo.tools import image_process


# class JsonRPCDispatcher(JsonRPCDispatcher):
#
#     def _response(self, result=None, error=None):
#         response = {}
#         if error is not None:
#             response['error'] = error
#             response['success'] = False
#             response['msg'] = error
#         if result is not None:
#             if not isinstance(result, bool) and not isinstance(result, int):
#                 if 'success' in result:
#                     if 'successful' in result:
#                         response['result'] = result
#                         response['msg'] = "Success"
#                         response['success'] = True
#                     elif result['success'] == False:
#                         response['success'] = False
#                         response['msg'] = result['msg']
#                         response['result'] = result
#                     elif result['success'] != False:
#                         response['result'] = result
#                         response['msg'] = "Success"
#                         response['success'] = True
#                 else:
#                     if 'error' in result:
#                         response['result'] = result['error']
#                         response['msg'] = result['error']
#                         response['success'] = False
#                     else:
#                         response['result'] = result
#                         response['msg'] = "Success"
#                         response['success'] = True
#             else:
#                 response['result'] = result
#                 response['msg'] = "Success"
#                 response['success'] = True
#         else:
#             # response['result'] = result
#             response['msg'] = "Faild"
#             response['success'] = False
#
#         return self.request.make_json_response(response)

#
def application_unproxied(environ, start_response):
    """ WSGI entry point."""
    if environ['REQUEST_METHOD'] == "OPTIONS":
        print(environ["REQUEST_METHOD"])
        response = werkzeug.wrappers.Response('OPTIONS METHOD DETECTED')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Max-Age'] = 1000
        response.headers['Access-Control-Allow-Headers'] = 'origin, * , x-csrftoken, content-type, accept'
        return response(environ, start_response)
    if hasattr(threading.current_thread(), 'uid'):
        del threading.current_thread().uid
    if hasattr(threading.current_thread(), 'dbname'):
        del threading.current_thread().dbname
    if hasattr(threading.current_thread(), 'url'):
        del threading.current_thread().url

    result = odoo.http.root(environ, start_response)
    if result is not None:
        return result

    return werkzeug.exceptions.NotFound("No handler found.\n")(environ, start_response)


wsgi_server.application_unproxied = application_unproxied





class AuthPortal(http.Controller):



    def get_image_url(self, model, res_id, field):
        attachment = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', model), ('res_field', '=', field), ('res_id', '=', res_id)])
        attachment.public = True
        attachment_url = attachment.local_url
        return attachment_url

    @http.route('/api/session/authenticate', type='json', cors="*", methods=["POST"], auth="public")
    def authenticate(self, db, login, password, base_location=None):
        response = self._web_login(db, login, password)
        if response.get('image_1920'):
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = response['image_1920']
            parts = url.split("?")[1].split("&")
            model, id, field = "", "", ""
            for part in parts:
                if part.startswith("id="):
                    id = part.split("=")[1]
                elif part.startswith("field="):
                    field = part.split("=")[1]
            partner_id = request.env['res.users'].sudo().search([('id', '=', id)]).partner_id
            image_url = self.get_image_url(partner_id._name,partner_id.id,field)
            if image_url:
                response['image_1920'] = base_url+image_url
            else:
                response['image_1920'] = False
        return response



    def _web_login(self, db, login, password):#, device_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web/session/authenticate'
        headers = {'Content-Type': 'application/json'}
        data = {"params": {"db": db, "login": login, "password": password, "device_id": False}}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:

                response_body = response.json()
                if 'error' in response_body:
                    response_body['result']['success'] = False
                    response_body['success'] = False
                    response_body['msg'] = response_body['error']['data']['arguments']
                    return response_body
                response_body['result']['success'] = True
                response_body['success'] = True
                cookies = response.cookies.get_dict()
                session_id = cookies.get('session_id', False)
                if session_id and response_body:
                    uid = response_body['result']['uid']
                    res = response_body['result']
                    user = http.request.env['res.users'].sudo().search([("id", "=", uid)], limit=1)
                    # if not user.device_id:
                    #     user.device_id = device_id
                    # elif user.device_id != device_id:
                    #     return {"success": False, "msg": "You Already Login With Other Device "}
                    res.update({'session_id': session_id,
                                "user_id": user.id,
                                'name': user.name,
                                # 'last_name': user.last_name,
                                'mobile': user.mobile,
                                "image_1920": request.httprequest.host_url + 'web/image?model=%s&id=%s&field=%s' % (
                                    "res.users", user.id, "image_1920")})
                    return res
            else:
                raise Exception("Authentication failed")
        except Exception as e:
            return {"success": False, "msg": "Could not perform login " + str(e) + "."}


class Product(http.Controller):

    #######################################33
    @http.route("/api/barcode/product", auth='user', type='json', methods=['POST'], csrf=False, cors="*")
    def api_search_product_barcode(self, **kw):
        """{
           "params": {
               "barcode": 3,

           }
       }"""
        response = {}
        if not kw:

            response.update({'msg': "no data", 'code': 400, 'success': False, 'result': []})
            return response
        elif not kw.get('barcode',False):
            response.update({'msg': "barcode dose not exist", 'code': 400, 'success': False, 'result': []})
            return response


        else:
            response = {}
            domain = [('active', '=', True), ('barcode', '=', kw.get('barcode',False)), ('barcode', '!=',False)]
            print('kw', kw)
            print('domain', domain)
            products = request.env['product.template'].sudo().search(domain, )
            print('products', products)
            data = [self.get_product_data(product) for product in products]
            if data:
                response.update({"msg": "Product data", "code": 200, 'success': True, 'data': data})
                return response
            else:

                response.update({'msg': "no data", 'code': 400, 'success': False, 'data': [{}]})
                return response


    def get_product_data(self, product):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {

            'id': product.id,
            'name': product.name,
            'Reference': product.default_code,
            'Barcode': product.barcode,
            # 'on_hand': available_quantity,
            'sale_price': product.list_price,

        }

