from dataclasses import dataclass
from flask import jsonify
from server import db
from sqlalchemy import ForeignKey
from server.models.recommendation_model import SimilarityModel

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

def get_products(page_size, paging, requirement = {}):
    product_query = None
    if ("category" in requirement):
        category = requirement.get("category")
        if (category == 'all'):
            product_query = Product.query.filter_by(source = 'native')
        else:
            product_query = Product.query.filter_by(source = 'native', category = category)
    elif ("keyword" in requirement):
        product_query = Product.query.filter_by(source = 'native').filter(Product.title.like(f"%{requirement.get('keyword')}%"))
    elif ("id" in requirement):
        product_query = Product.query.filter_by(id = requirement.get("id"))
    elif ("source" in requirement):
        product_query = Product.query.filter_by(source = requirement.get("source"))
    elif ("recommend" in requirement):
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