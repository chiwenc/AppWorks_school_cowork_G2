from server import db
import random
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    picture = db.Column(db.String(512))

    def __repr__(self):
        return '<User {}>'.format(self.username)

                        
def get_products(page_size, paging, requirement = {}):

    u = User(username='susan', email='susan@example.com')
    print(u)
    # print("Get product")

    # cursor = db.engine.execute('SELECT * FROM product WHERE source = "native" AND category = %s LIMIT 2', ["men"])
    # print(cursor)
    # print(cursor.keys())
    # print(cursor.fetchall())

    return "YA"
    # condition = {"sql": 'WHERE source = "native"', "binding": []}
    # if ("category" in requirement):
    #     condition["sql"] = 'WHERE category = %s AND source = "native"'
    #     condition["binding"] = [requirement.get("category")]
    # elif ("keyword" in requirement):
    #     condition["sql"] = 'WHERE title LIKE %s AND source = "native"'
    #     condition["binding"] = [f"%{requirement.get('keyword')}%"]
    # elif ("id" in requirement):
    #     condition["sql"] = 'WHERE id = %s'
    #     condition["binding"] = [requirement.get("id")]
    # elif ("source" in requirement):
    #     condition["sql"] = 'WHERE source = %s'
    #     condition["binding"] = [requirement.get("source")]
    # elif ("recommend" in requirement):
    #     condition["sql"] = ' \
    #         INNER JOIN similarity_model ON product.id = similarity_model.item2_id \
    #         WHERE similarity_model.item1_id = %s \
    #         ORDER BY similarity DESC \
    #     '
    #     condition["binding"] = [requirement.get("recommend")]

    # limit = {
    #     'sql': 'LIMIT %s, %s',
    #     'binding': [page_size * paging, page_size]
    # }

    # product_query = 'SELECT * FROM product ' + condition["sql"] + limit["sql"]
    # product_bindings = condition["binding"] + limit["binding"]
    # cursor = db.engine.execute(product_query, product_bindings)
    # products = cursor.fetchall()

    # product_count_query = 'SELECT COUNT(*) as count FROM product ' + condition["sql"]
    # product_count_bindings = condition["binding"]
    # cursor = db.engine.execute(product_count_query, product_count_bindings)
    # product_count = cursor.fetchone()["count"]

    # return {
    #     "products": products,
    #     "product_count": product_count
    # }

def get_products_variants(product_ids):
    # cursor = conn.cursor()
    query = f"SELECT * FROM variant WHERE product_id IN ({','.join([str(id) for id in product_ids])})"
    cursor = db.engine.execute(query)
    variants = cursor.fetchall()
    # conn.commit()
    return variants

def create_product(product, variants):
    cursor = conn.cursor()
    columns = ','.join([f"`{key}`" for key in product.keys()])
    bindings = ','.join(['%s' for i in range(len(product))])
    insert_product_sql = f" \
        INSERT INTO product ( \
            {columns} \
        ) VALUES ( \
            {bindings} \
        ) \
    "
    cursor.execute(insert_product_sql, list(product.values()))

    columns = ','.join([f"`{key}`" for key in variants[0].keys()])
    bindings = ','.join(['%s' for i in range(len(variants[0]))])
    insert_variant_sql = f" \
        INSERT INTO variant ({columns}) \
        VALUES({bindings}) \
    "
    cursor.executemany(insert_variant_sql, [list(v.values()) for v in variants])

    conn.commit()  