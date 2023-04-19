import json
import random

import requests

import pandas as pd
import json

# Create your views here.
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.schemas import get_schema_view, openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.views import *
from drf_yasg import  *
from io import BytesIO
from PIL import Image, ImageDraw
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view



@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, World!'})
#測試1
@swagger_auto_schema(methods=['post'], request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'age', 'gender'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'age': openapi.Schema(type=openapi.TYPE_INTEGER),
        'gender': openapi.Schema(type=openapi.TYPE_STRING),

    }
))
@api_view(['POST'])
def add_person(request):
    """
    Add a person to the database.
    """
    name = request.data.get('name', '')
    age = request.data.get('age', '')
    gender = request.data.get('gender', '')
    # 在這裡可以對參數進行處理和驗證
    # 返回一個JSON響應，包含提交的參數
    message = f'{name} added successfully.'
    return Response({'status': 'success', 'message': message, 'name': name, 'age': age, 'gender': gender})


#提供類別 返回各縣市數量
gender_enum = openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=['貓', '狗']
)

@swagger_auto_schema(methods=['post'], request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['kind'],
    properties={

        'kind': gender_enum,
    }
))
@api_view(['POST'])
def Query_Qty(request):
    gender_enum_list = ['貓', '狗']
    gender = request.data.get('kind', '未輸入資料')

    if gender not in gender_enum_list:
        return Response({'status': '錯誤', 'message': '輸入的資料不在列表 貓/狗'})
    else :
        url = "https://data.coa.gov.tw/Service/OpenData/TransService.aspx?UnitId=QcbUEzN6E6DL"

        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        # 只留下縣市名稱
        df['shelter_address'] = df['shelter_address'].str[:3]

        # 篩選動物種類，並計算各縣市的數量
        ami_count = df[df['animal_kind'] == gender]['shelter_address'].value_counts().sort_index()
        ami_count_dict = ami_count.to_dict()
        print(ami_count)
        message =  'Query_Qty  successfully.'
        return Response({'status': 'success',
                         'message': message,
                         'gender': gender ,
                         'count' : ami_count_dict
                         })


gender_enum = openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=['貓', '狗'],
    default='貓',
    description='動物類型',
)


count = openapi.Schema(
    type=openapi.TYPE_INTEGER,
    default=30,
    description='圖片數量',
)


@swagger_auto_schema(methods=['post'], request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['kind', 'count'],
    properties={
        'kind': gender_enum,
        'count': count,
    }
))
@api_view(['POST'])
def image_wall(request):
    # 從 OpenData 取得資料，並轉換成 DataFrame
    response = requests.get("https://data.coa.gov.tw/Service/OpenData/TransService.aspx?UnitId=QcbUEzN6E6DL")
    data = response.json()
    df = pd.DataFrame(data)

    # 接收參數，判斷動物類型
    animal_type = request.data.get('kind', '貓')

    if animal_type not in ['貓', '狗']:
        animal_type = '貓狗'

    # 取得圖片 URL 列表，僅保留與狗或貓相關的圖片
    if animal_type == '貓':
        img_urls = df[df['animal_kind'] == '貓']['album_file'].tolist()
    elif animal_type == '狗':
        img_urls = df[df['animal_kind'] == '狗']['album_file'].tolist()
    else:
        img_urls = df[df['animal_kind'].isin(['狗', '貓'])]['album_file'].tolist()
    #亂數產出
    random.shuffle(img_urls)
    # 取得圖片數量
    count = request.data.get('count', 30)

    try:
        count = int(count)
        if count <= 0:
            count = 30
    except ValueError:
        count = 30
    img_count = count
    # 迭代圖片 URL 列表，將前 count 個加入圖片列表
    images = []
    for img_url in img_urls:
        if img_url.endswith('.jpg') or img_url.endswith('.png'):
            images.append(f'<li><img src="{img_url}" width="100" height="100"></li>')
            if len(images) == count:
                break

    # 創建 HTML 列表
    html = f'<ul style="list-style:none; display: flex; flex-wrap: wrap;">{"".join(images)}</ul>'
    html_json = json.dumps({'html': html})
    # 將 HTML 轉換為 JSON 格式
    html = html_json.replace('\\', '')  # 去除跳脫字符 \
    html_output = html.replace('\"', '"')  # 去除跳脫字符 "


    # 返回 JSON 格式的回應
    return HttpResponse(html_output, content_type='application/json')




schema_view = get_schema_view(
    openapi.Info(
        title="My Project",
        default_version='v1',
        description="My Project API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myproject.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

