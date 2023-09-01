import requests
import json
import pymysql
import logging
import os

from config import Config

my_db_conf = Config()


# Config: Logger
log_name = "get-original-data"
log_dire = "log"
log_path = log_dire + "/" + log_name
os.makedirs(log_dire, exist_ok=True)
this_logger = logging.getLogger(__name__)
this_logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s")

file_handler = logging.FileHandler(log_path, mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(log_formatter)

this_logger.addHandler(file_handler)
this_logger.addHandler(stream_handler)


# Male: 3, Female: 8, Accessory:4
def get_product():
    all_data = []
    url = "https://api.appworks-school.tw/api/1.0/products/all?paging=0"
    response = json.loads(requests.get(url).text)
    # print(response["data"])
    all_data.append(response["data"])
    while "next_paging" in response.keys():
        url = f"https://api.appworks-school.tw/api/1.0/products/all?paging={response['next_paging']}"
        response = json.loads(requests.get(url).text)
        all_data.append(response["data"])

    # this_logger.info(all_data[0][0])
    # print(len(all_data[0][0]))
    print(all_data[0])
    return all_data


def insert_to_db(data: list):
    conn = pymysql.connect(**my_db_conf.db_config)
    with conn.cursor() as cursor:
        insert_product_sql = ("INSERT INTO `product` (`id`, `category`, `title`, `description`, `price`, `texture`, `wash`, "
                              "`place`, `note`, `story`, `main_image`, `images`) "
                              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        insert_variant_sql = ("INSERT INTO `variant` (`color_code`, `color_name`, `size`, `stock`, `product_id`) "
                              "VALUES (%s,%s,%s,%s,%s)")
        color_dict = {}
        for page in data:
            for _ in page:
                _id = _["id"]
                _category = _["category"]
                _title = _["title"]
                _description = _["description"]
                _price = _["price"]
                _texture = _["texture"]
                _wash = _["wash"]
                _place = _["place"]
                _note = _["note"]
                _story = _["story"]
                _main_image = _["main_image"]
                _images = ', '.join(_["images"])
                _colors = _["colors"]
                for color in _colors:
                    color_dict.update({color["code"]: color["name"]})
                _variants = _["variants"]
                for each in _variants:
                    _size = each["size"]
                    _color_code = each["color_code"]
                    _stock = each["stock"]
                    _color_name = color_dict[_color_code]
                    cursor.execute(insert_variant_sql,
                                   (_color_code, _color_name, _size, _stock, _id))
                cursor.execute(insert_product_sql,
                               (_id, _category, _title, _description, _price, _texture, _wash, _place, _note,
                                _story, _main_image, _images))

        conn.commit()


all_items = get_product()
insert_to_db(data=all_items)

