# -*- coding: utf-8 -*-
import re

example_template = '''
# -*- coding: utf-8 -*-
from odoo.http import request
from datetime import datetime, date
import json
import base64
from odoo import http
from datetime import datetime
def Success(message="成功！", data=''):
    response_data = json.dumps({
        "status": 200,
        "message": message,
        "data": data
    })
    return http.Response(response_data, status=200, mimetype='application/json')


def Failure(message="失败！", data=''):
    response_data = json.dumps({
        "status": 400,
        "message": message,
        "data": data
    })
    return http.Response(response_data, status=400, mimetype='application/json')

class VehicleController(http.Controller):
    @http.route('/query_vehicle/<int:vehicle_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def query_vehicle(self, vehicle_id):
        vehicle = request.env['vehicle'].sudo().browse(vehicle_id)
        if not vehicle.exists():
            return Failure('数据不存在！')

        context = {}
        context.update(vehicle.read()[0])

        # 转换datetime字段
        for key, value in context.items():
            if isinstance(value, datetime):
                context[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # 转换为字符串格式

        if vehicle and hasattr(vehicle,'image'):
            del context['image']
            context['image_url'] = '/vehicle/image/%s' % vehicle_id  # Generate image URL

        return Success("获取成功！",data=context)

    @http.route('/upload_vehicle', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def upload_vehicle(self, **kwargs):
        values = {key: kwargs[key] for key in kwargs}

        # Check if 'image' is in the uploaded files
        if 'image' in request.httprequest.files:
            image_file = request.httprequest.files['image']
            image_data = image_file.read()
            # Encode the image to base64
            values['image'] = base64.b64encode(image_data)

        new_vehicle = request.env['vehicle'].sudo().create(values)
        return Success("上传成功！")

    @http.route('/<model_name>/<int:record_id>/images', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all_images(self, model_name, record_id, **kwargs):
        # 将模型名称中的点号替换为下划线
        model_name = model_name.replace('_', '.')

        # 获取记录
        record = request.env[model_name].sudo().browse(record_id)

        # 检查记录是否存在
        if not record:
            return request.not_found()

        # 查找所有二进制字段
        binary_fields = {field: field_def for field, field_def in record.fields_get().items() if
                         field_def['type'] == 'binary'}

        # 生成每个二进制字段的 URL
        media_urls = {}
        for field, field_def in binary_fields.items():
            media_urls[field] = f'/{model_name.replace(".", "_")}/{record_id}/media/{field}'

        return Success("媒体列表获取成功！", data=media_urls)

    @http.route('/<model_name>/<int:record_id>/media/<string:field_name>', type='http', auth='public', methods=['GET'],csrf=False)
    def get_media_field(self, model_name, record_id, field_name, **kwargs):
        # 将模型名称中的下划线替换为点号
        model_name = model_name.replace('_', '.')

        # 获取记录
        record = request.env[model_name].sudo().browse(record_id)

        # 检查记录是否存在和字段是否为二进制字段
        if not record or field_name not in record.fields_get() or record.fields_get()[field_name]['type'] != 'binary':
            return request.not_found()

        # 获取媒体数据
        media_data = getattr(record, field_name, None)
        if not media_data:
            return request.not_found()

        # 解码 Base64 数据
        try:
            media_data = base64.b64decode(media_data)
        except Exception as e:
            return request.not_found()  # 处理解码错误

        # 确定媒体类型并设置正确的 MIME 类型
        field_def = record.fields_get()[field_name]
        content_type = 'application/octet-stream'  # 默认类型
        if field_name == 'image':
            content_type = 'image/png'
        elif field_name == 'video':
            content_type = 'video/mp4'  # 假设视频格式为 mp4
        elif field_name == 'audio':
            content_type = 'audio/mpeg'  # 假设音频格式为 mp3

        # 返回媒体内容
        return request.make_response(media_data, headers=[('Content-Type', content_type)])

    @http.route('/delete_vehicle/<int:vehicle_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def delete_vehicle(self, vehicle_id):
        vehicle = request.env['vehicle'].sudo().browse(vehicle_id)
        if not vehicle.exists():
            return Failure("数据不存在！")
        vehicle.sudo().unlink()
        return Success("删除成功！")


    @http.route('/list_vehicle_pages', type='http', auth='public', methods=['GET'], csrf=False)
    def list_vehicle_pages(self,**kw):
        # 获取页码和每页条目数量，默认为1和10
        page = int(kw.get('page', 1))
        per_page = int(kw.get('per_page', 10))

        offset = (page - 1) * per_page
        limit = per_page

        vehicles = request.env['vehicle'].sudo().search([], offset=offset, limit=limit) # # order='start_time DESC'
        context = []
        for vehicle in vehicles:
            item = {'image_url': ''}
            item.update(vehicle.read()[0])

            # 获取字典的键列表，避免遍历时修改字典导致的错误
            for key in list(item.keys()):
                value = item[key]

                # 删除二进制字段
                if isinstance(value, bytes):
                    del item[key]
                    # 生成图像 URL
                    item[key] = f'/{key}/image/%s' % vehicle.id  # 生成图像 URL

                # 删除关联字段（以 _id 或 _ids 结尾）
                elif key.endswith("_id") or key.endswith("_ids"):
                    del item[key]

                # 转换 datetime 字段为字符串格式
                elif isinstance(value, datetime):
                    item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, date):
                    item[key] = value.strftime("%Y-%m-%d")  # 处理 date 类型字段
            context.append(item)

        return Success("获取成功！", data=context)

    @http.route('/list_vehicle_pages', type='http', auth='public', methods=['GET'], csrf=False)
    # def list_vehicle_pages(self,**kw):
    #     # 获取页码和每页条目数量，默认为1和10
    #     page = int(kw.get('page', 1))
    #     per_page = int(kw.get('per_page', 10))
    # 
    #     offset = (page - 1) * per_page
    #     limit = per_page
    # 
    #     vehicles = request.env['vehicle'].sudo().search([], offset=offset, limit=limit) # # order='start_time DESC'
    #     context = []
    #     fields_to_return = ['id', 'dc', '自定义字段']
    #     for vehicle in vehicles:
    #         item = {}
    #         data = vehicle.read()[0]
    #         for field in fields_to_return:
    #             if field in data:
    #                 item[field] = data[field]
    #         for key, value in item.items():
    #             if isinstance(value, datetime):
    #                 item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    #             elif isinstance(value, date):
    #                 item[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    #         if vehicle and hasattr(vehicle, 'image'):
    #             del item['image']
    #             item['image_url'] = '/vehicle/image/%s' % vehicle.id
    #         context.append(item)
    #     return Success("获取成功！", data=context)



    @http.route('/update_vehicle/<int:vehicle_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def update_vehicle(self, vehicle_id, **kwargs):
        vehicle = request.env['vehicle'].sudo().browse(vehicle_id)
        if not vehicle.exists():
            return Failure("数据不存在！")

        # 预处理参数
        values = {}
        for key, value in kwargs.items():
            if key in ['activity_state']:
                values[key] = value.lower() == 'true'  # 转换为布尔值
            elif isinstance(value, str) and value.lower() in ['true', 'false']:
                values[key] = value.lower() == 'true'  # 处理其他布尔字段
            elif isinstance(value, str) and 'T' in value:  # 检测 ISO 8601 格式
                try:
                    values[key] = datetime.fromisoformat(value)  # 转换为 datetime 对象
                except ValueError as e:
                    return Failure(f"无效的日期格式: {str(e)}")
            elif key == 'activity_ids' and not value:
                continue  # 跳过空列表
            else:
                values[key] = value

        # Check if 'image' is in the uploaded files
        if 'image' in request.httprequest.files:
            image_file = request.httprequest.files['image']
            image_data = image_file.read()
            # Encode the image to base64
            values['image'] = base64.b64encode(image_data)

        vehicle.sudo().write(values)

        # Update the image URL if necessary
        # image_url = '/vehicle/image/%s' % vehicle_id
        # vehicle.sudo().write({'image_url': image_url})

        return Success("更新成功！")

    @http.route('/get_vehicle_field/<int:vehicle_id>/<field_name>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_field_value(self, vehicle_id, field_name):
        vehicle = request.env['vehicle'].sudo().browse(vehicle_id)
        if not vehicle.exists():
            return Failure('数据不存在！')

        if not hasattr(vehicle, field_name):
            return Failure(f'字段 {field_name} 不存在！')

        field_value = getattr(vehicle, field_name)

        # 转换datetime字段
        if isinstance(field_value, datetime):
            field_value = field_value.isoformat()

        return Success("获取成功！", data={field_name: field_value})'''

image_example = '''
if charging_device and hasattr(charging_device, 'image'):
    del context['image']
    context['image_url'] = '/charging_device/image/%s' % charging_device_id  # Generate image URL'''



# 生成代码函数
def generate_code(class_name:str, model_name:str):
    global example_template,image_example
    example_template = example_template.replace('vehicle', class_name.lower())
    example_template = example_template.replace('Vehicle', class_name.capitalize())
    pattern = "request.env\['(.*?)'\]"
    # 正则替换
    example_template = re.sub(pattern, "request.env['%s']" % model_name, example_template)
    return example_template

if __name__=="__main__":
    class_name = "BlogPost"  # 需要修改为类名
    model_name = "blog.post"  # 需要修改为实际模型名
    example_template = generate_code(class_name, model_name)
    print(example_template)
