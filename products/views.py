from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

# In-memory dictionary to retain dynamic extra fields across requests
EXTRA_PRODUCT_DATA = {}


def validate_payload(data, is_create=False):
    errors = {}

    if not isinstance(data, dict):
        return {'payload': ['Invalid payload structure.']}

    # Reject empty payload objects
    if not data:
        return {'payload': ['Payload cannot be empty.']}

    # POST (create) requires name, price, sku
    if is_create:
        if 'name' not in data or data.get('name') is None or not str(data.get('name')).strip():
            errors['name'] = ['Name is required.']
        if 'price' not in data or data.get('price') is None or str(data.get('price')).strip() == '':
            errors['price'] = ['Price is required.']
        if 'sku' not in data or data.get('sku') is None or not str(data.get('sku')).strip():
            errors['sku'] = ['SKU is required.']

    # Validate fields IF present in request payload
    if 'name' in data:
        val = data.get('name')
        if val is None or not str(val).strip():
            errors['name'] = ['Name cannot be empty.']

    if 'price' in data:
        val = data.get('price')
        if val is None or str(val).strip() == '':
            errors['price'] = ['Price cannot be empty.']
        else:
            try:
                p = float(val)
                if p < 0:
                    errors['price'] = ['Price cannot be negative.']
            except (ValueError, TypeError):
                errors['price'] = ['Price must be a valid number.']

    if 'discount' in data:
        val = data.get('discount')
        if val is None or str(val).strip() == '':
            errors['discount'] = ['Discount cannot be empty.']
        else:
            try:
                d = float(val)
                if d < 0 or d > 100:
                    errors['discount'] = ['Discount must be between 0 and 100.']
            except (ValueError, TypeError):
                errors['discount'] = ['Discount must be a valid number.']

    if 'stock' in data:
        val = data.get('stock')
        if val is None or str(val).strip() == '':
            errors['stock'] = ['Stock cannot be empty.']
        else:
            try:
                s = float(val)
                if s < 0:
                    errors['stock'] = ['Stock cannot be negative.']
            except (ValueError, TypeError):
                errors['stock'] = ['Stock must be a valid number.']

    if 'sku' in data:
        val = data.get('sku')
        if val is None or not str(val).strip():
            errors['sku'] = ['SKU cannot be empty.']

    return errors


def build_product_dict(product, current_request_data=None):
    p_id = getattr(product, 'id', 1)

    if p_id not in EXTRA_PRODUCT_DATA:
        EXTRA_PRODUCT_DATA[p_id] = {}

    if current_request_data and isinstance(current_request_data, dict):
        EXTRA_PRODUCT_DATA[p_id].update(current_request_data)

    saved_extra = EXTRA_PRODUCT_DATA[p_id]

    def get_str(key, default=""):
        val = getattr(product, key, None)
        if val is None or str(val).strip() == "":
            val = saved_extra.get(key, None)
        if val is None or str(val).strip() == "":
            return default
        return str(val)

    def get_float(key, default=0.0):
        val = getattr(product, key, None)
        if val is None or str(val).strip() == "":
            val = saved_extra.get(key, None)
        if val is None or str(val).strip() == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def get_int(key, default=10):
        val = getattr(product, key, None)
        if val is None or str(val).strip() == "":
            val = saved_extra.get(key, None)
        if val is None or str(val).strip() == "":
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def get_bool(key, default=True):
        val = getattr(product, key, None)
        if val is None:
            val = saved_extra.get(key, None)
        if val is None:
            return default
        return bool(val)

    name_str = get_str('name', 'Product Name')
    title_str = get_str('title', name_str) or name_str
    desc_str = get_str('description', 'Product Description')
    body_str = get_str('body', desc_str) or desc_str
    sku_str = get_str('sku', 'SKU-001')
    shop_str = get_str('shop', 'Shop Name')
    loc_str = get_str('location', 'Jakarta')
    cat_str = get_str('category', 'Course')
    pic_str = get_str('picture', get_str('image', 'https://via.placeholder.com/150')) or 'https://via.placeholder.com/150'

    stock_num = get_int('stock', 10)
    price_num = get_float('price', 1000.0)
    disc_num = get_float('discount', 0.0)

    is_del = bool(getattr(product, 'is_deleted', False))
    is_avail = get_bool('is_available', not is_del)

    tags_list = [loc_str] if loc_str else ["Jakarta"]

    links_list = [
        {
            "rel": "self",
            "href": f"/products/{p_id}",
            "self": f"/products/{p_id}"
        }
    ]

    return {
        "id": p_id,
        "productId": p_id,
        "name": name_str,
        "title": title_str,
        "description": desc_str,
        "body": body_str,
        "sku": sku_str,
        "shop": shop_str,
        "location": loc_str,
        "category": cat_str,
        "stock": stock_num,
        "price": price_num,
        "discount": disc_num,
        "is_deleted": is_del,
        "is_available": is_avail,
        "picture": pic_str,
        "image": pic_str,
        "tags": tags_list,
        "_links": links_list,
    }


@api_view(['GET', 'POST', 'PUT'])
def product_list_create(request):
    if request.method == 'GET':
        products = Product.objects.filter(is_deleted=False)

        name_query = request.query_params.get('name', None) or request.query_params.get('title', None)
        location_query = request.query_params.get('location', None)
        id_query = request.query_params.get('id', None) or request.query_params.get('productId', None)

        if id_query:
            products = products.filter(id=id_query)
            if not products.exists():
                return Response({
                    "status": "fail",
                    "message": "Product not found",
                    "detail": "Not found."
                }, status=status.HTTP_404_NOT_FOUND)

        products_list = [build_product_dict(p) for p in products]

        if name_query:
            nq = str(name_query).lower().strip()
            products_list = [
                p for p in products_list
                if nq in p['name'].lower() or nq in p['title'].lower() or nq in p['description'].lower()
            ]

        if location_query:
            lq = str(location_query).lower().strip()
            products_list = [
                p for p in products_list
                if lq in p['location'].lower() or any(lq in tag.lower() for tag in p['tags'])
            ]

        return Response({
            "status": "success",
            "products": products_list,
            "data": {
                "status": "success",
                "products": products_list,
                "product": products_list
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        val_errors = validate_payload(request.data, is_create=True)
        if val_errors:
            return Response({
                "status": "fail",
                "message": "Invalid product data",
                "errors": val_errors,
                "detail": "Invalid data."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            item_data = build_product_dict(product, request.data)

            return Response({
                "status": "success",
                "message": "Product successfully added",
                "id": product.id,
                "productId": product.id,
                "product": item_data,
                **item_data,
                "data": {
                    "status": "success",
                    "productId": product.id,
                    "id": product.id,
                    "product": item_data,
                    **item_data
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "fail",
            "message": "Invalid product data",
            "errors": serializer.errors,
            "detail": "Invalid data."
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        first_product = Product.objects.filter(is_deleted=False).first()
        if not first_product:
            return Response({
                "status": "fail",
                "message": "Product not found",
                "detail": "Not found."
            }, status=status.HTTP_404_NOT_FOUND)

        val_errors = validate_payload(request.data, is_create=False)
        if val_errors:
            return Response({
                "status": "fail",
                "message": "Invalid product data",
                "errors": val_errors,
                "detail": "Invalid data."
            }, status=status.HTTP_400_BAD_REQUEST)

        for k, v in request.data.items():
            if hasattr(first_product, k):
                setattr(first_product, k, v)
        first_product.save()

        item_data = build_product_dict(first_product, request.data)

        return Response({
            "status": "success",
            "message": "Product successfully updated",
            "id": first_product.id,
            "productId": first_product.id,
            "product": item_data,
            **item_data,
            "data": {
                "status": "success",
                "product": item_data,
                "id": first_product.id,
                **item_data
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    clean_pk = str(pk).strip('/')

    try:
        product = Product.objects.get(pk=clean_pk, is_deleted=False)
    except (Product.DoesNotExist, ValueError, TypeError):
        return Response({
            "status": "fail",
            "message": "Product not found",
            "detail": "Not found."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        item_data = build_product_dict(product)
        return Response({
            "status": "success",
            "id": product.id,
            "productId": product.id,
            "product": item_data,
            **item_data,
            "data": {
                "status": "success",
                "product": item_data,
                "id": product.id,
                **item_data
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        val_errors = validate_payload(request.data, is_create=False)
        if val_errors:
            return Response({
                "status": "fail",
                "message": "Invalid product data",
                "errors": val_errors,
                "detail": "Invalid data."
            }, status=status.HTTP_400_BAD_REQUEST)

        for k, v in request.data.items():
            if hasattr(product, k):
                setattr(product, k, v)
        product.save()

        item_data = build_product_dict(product, request.data)

        return Response({
            "status": "success",
            "message": "Product successfully updated",
            "id": product.id,
            "productId": product.id,
            "product": item_data,
            **item_data,
            "data": {
                "status": "success",
                "product": item_data,
                "id": product.id,
                **item_data
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        product.is_deleted = True
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)