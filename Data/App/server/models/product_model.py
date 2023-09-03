from dataclasses import dataclass
from flask import jsonify
from server import db
from sqlalchemy import ForeignKey
from ..models.recommendation_model import SimilarityModel


class Product(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    category = db.Column(db.String(127), index=True)
    title = db.Column(db.String(255), index=True)
    description = db.Column(db.String(255))
    price = db.Column(db.Integer)
    texture = db.Column(db.String(127))
    wash = db.Column(db.String(127))
    place = db.Column(db.String(127))
    note = db.Column(db.String(127))
    story = db.Column(db.Text())
    main_image = db.Column(db.String(255))
    images = db.Column(db.String(255))
    source = db.Column(db.String(127))
    image_base64 = db.Column(db.Text())

    def __repr__(self):
        return '<Product {}, {}, {}>'.format(self.id, self.category, self.title)


class Variant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color_code = db.Column(db.String(15))
    color_name = db.Column(db.String(15))
    size = db.Column(db.String(15))
    stock = db.Column(db.Integer)
    product_id = db.Column(db.String(200), db.ForeignKey('product.id'))

    def __repr__(self):
        return '<Variant {}>'.format(self.id)

class OrderHistory(db.Model):
    auto_id = db.Column(db.String(200), primary_key=True)
    order_id = db.Column(db.String(127))
    order_time = db.Column(db.Integer)
    user_id = db.Column(db.String(255))
    product_id = db.Column(db.String(255))
    prime = db.Column(db.String(255))
    shipping = db.Column(db.String(255))
    payment = db.Column(db.String(255))
    subtotal = db.Column(db.Integer)
    freight = db.Column(db.Integer)
    total = db.Column(db.Integer)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(127))
    email = db.Column(db.String(127))
    address = db.Column(db.String(127))
    time = db.Column(db.String(127))
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(127))
    price = db.Column(db.String(127))
    color_name = db.Column(db.String(15))
    color_code = db.Column(db.String(127))
    size = db.Column(db.String(15))
    qty = db.Column(db.String(127))

    def __repr__(self):
        return f"<OrderHistory(auto_id='{self.auto_id}', order_id='{self.order_id}', product_id='{self.product_id}', user_id='{self.user_id}')>"

def get_all_order_history(user_id):
    try:
        order_history = OrderHistory.query.filter_by(user_id=user_id).all()
        histories = []

        for order in order_history:
            order_id = order.order_id

            # Convert the order_time (assuming it's a Unix timestamp) to the desired string format
            order_time = order.order_time.strftime('%Y/%m/%d')

            # Check if this order_id has already been processed
            existing_entry = next((entry for entry in histories if entry["order_id"] == order_id), None)

            if existing_entry is None:
                history_entry = {
                    "order_id": order_id,
                    "total": order.total,
                    "time": order_time,
                    "products": []
                }

                product_data = {
                    "address": order.address,
                    "color": order.color_code,
                    "name": order.name,
                    "phone": order.phone,
                    "price": order.price,
                    "qty": order.qty,
                    "size": order.size,
                    "title": order.product_name,
                }

                # Fetch main_image for the associated product using a separate query
                product = Product.query.filter_by(id=order.product_id).first()
                if product:
                    product_data["main_image"] = product.main_image
                else:
                    product_data["main_image"] = None

                history_entry["products"].append(product_data)
                histories.append(history_entry)
            else:
                product_data = {
                    "address": order.address,
                    "color": order.color_code,
                    "name": order.name,
                    "phone": order.phone,
                    "price": order.price,
                    "qty": order.qty,
                    "size": order.size,
                    "title": order.product_name,
                }

                # Fetch main_image for the associated product using a separate query
                product = Product.query.filter_by(id=order.product_id).first()
                if product:
                    product_data["main_image"] = product.main_image
                else:
                    product_data["main_image"] = None

                existing_entry["products"].append(product_data)

        response_data = {
            "histories": histories
        }

        return response_data
    except Exception as e:
        error_message = str(e)
        response_data = {
            "error": "An error occurred while fetching order history",
            "details": error_message
        }

        return response_data

def get_products(page_size, paging, requirement={}):
    product_query = None
    if "category" in requirement:
        category = requirement.get("category")
        if category == 'all':
            product_query = Product.query.filter_by(source = 'native')
        else:
            product_query = Product.query.filter_by(source = 'native', category = category)
    elif "keyword" in requirement:
        product_query = Product.query.filter_by(source = 'native').filter(Product.title.like(f"%{requirement.get('keyword')}%"))
    elif "id" in requirement:
        product_query = Product.query.filter_by(id = requirement.get("id"))
    elif "source" in requirement:
        product_query = Product.query.filter_by(source = requirement.get("source"))
    elif "recommend" in requirement:
        product_query = Product.query.join(SimilarityModel, Product.id == SimilarityModel.item2_id)\
            .filter_by(item1_id = requirement.get("recommend"))\
            .order_by(SimilarityModel.similarity.desc())
        
    products = product_query.limit(page_size).offset(page_size * paging).all()
    count = product_query.count()

    return {
        "products": [p.to_json() for p in products],
        "product_count": count
    }


def get_products_variants(product_ids):
    variants = Variant.query.filter(Product.id.in_(product_ids)).all()
    return [v.to_json() for v in variants]


def create_product(product, variants):
    try:
        product_model = Product(**product)
        db.session.add(product_model)
        db.session.flush()

        db.session.bulk_insert_mappings(
            Variant,
            variants
        )
        db.session.commit()
    except Exception as e:
        print(e)