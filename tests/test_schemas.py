"""
Testing module for Marshmallow-JSONApi implementation on Peewee Models.
Tests run with no flask involvment and are used to check validation
of inputs (post/put request data) and output from the Schemas dump method, that
will be used as return value for Flask-Restful endpoint handlers.
"""
import copy
from datetime import datetime

import utils
from models import Address, Item, Order, Picture
from schemas import (AddressSchema, ItemSchema, OrderSchema, PictureSchema,
                     UserSchema)
from tests import test_utils
from tests.test_case import TestCase
from tests.test_utils import (RESULTS, add_address, add_user,
                              assert_valid_response, format_jsonapi_request)

USER_TEST_DICT = {
    "first_name": "Monty",
    "last_name": "Python",
    "email": "montsdf@asdhon.org",
    "password": "ewrwer"
}
EXPECTED_RESULTS = RESULTS['schemas']
EXPECTED_ORDERS = EXPECTED_RESULTS['orders']
EXPECTED_USERS = EXPECTED_RESULTS['users']
EXPECTED_ADDRESSES = EXPECTED_RESULTS['addresses']
EXPECTED_ITEMS = EXPECTED_RESULTS['items']
EXPECTED_PICTURES = EXPECTED_RESULTS['pictures']


TEST_IMAGE_FOLDER = 'test_images'


class TestUserSchema(TestCase):
    def setup_method(self):
        super(TestUserSchema, self).setup_method()
        # Setup the same mock database data for every test
        self.user1 = add_user(
            **USER_TEST_DICT,
            id='cfe57aa6-76c6-433d-93fe-443363978904',
        )
        self.addr1 = add_address(
            self.user1,
            id='e8c4607a-a271-423f-981b-1aaefdac87e8',
        )

        self.order1 = Order.create(delivery_address=self.addr1, user=self.user1,
                                   uuid='4cefa833-2f45-4662-b2fc-083ddad4f7a3',
                                   created_at=datetime(2017, 5, 1, 3, 5, 57),
                                   )
        self.order2 = Order.create(delivery_address=self.addr1, user=self.user1,
                                   uuid='8d449938-5745-4489-ab32-89dc8178e347',
                                   created_at=datetime(2017, 5, 1, 11, 16, 25),
                                   )

        # User 2 has no relationships, just a plain user
        self.user2 = add_user(
            first_name="Monty",
            last_name="Python",
            email="python@monty.org",
            password="ewrwer",
            id='94495ece-559b-4b3a-87ed-799259c921bf',
        )

    def test_user_json__success(self):
        parsed_user, errors = UserSchema.jsonapi(self.user2)
        expected_result = EXPECTED_USERS['user_json__success']

        assert type(parsed_user) is str

        assert_valid_response(parsed_user, expected_result)
        assert errors == {}

    def test_get_users_list_json__success(self):
        parsed = UserSchema.jsonapi_list([self.user1, self.user2])

        assert type(parsed) is str
        expected_result = EXPECTED_USERS['get_users_list_json__success']
        assert_valid_response(parsed, expected_result)

    def test_user_include_orders__success(self):
        parsed_user, _ = UserSchema.jsonapi(
            self.user1, include_data=['orders'])

        expected_result = EXPECTED_USERS['user_include_orders__success']
        assert_valid_response(parsed_user, expected_result)

    def test_user_validate_input__success(self):
        post_data = format_jsonapi_request('user', USER_TEST_DICT)

        errors = UserSchema.validate_input(post_data)
        assert errors == {}

    def test_user_validate_input__fail(self):
        wrong_user_data = USER_TEST_DICT.copy()
        del wrong_user_data['password']             # missing field validation
        wrong_user_data['last_name'] = ''           # empty field validation
        wrong_user_data['email'] = 'email.is.not'   # email validation

        post_data = format_jsonapi_request('user', wrong_user_data)

        errors = UserSchema.validate_input(post_data)

        expected_result = EXPECTED_USERS['user_validate_input__fail']
        assert_valid_response(errors, expected_result)


class TestOrderSchema(TestCase):
    def setup_method(self):
        super(TestOrderSchema, self).setup_method()
        # Mock data for tests
        self.user = add_user(
            **USER_TEST_DICT, id='cfe57aa6-76c6-433d-93fe-443363978904',
        )
        self.addr = add_address(
            self.user, id='27e375f4-3d54-458c-91e4-d8a4fdf3b032',
        )
        self.item1 = Item.create(
            uuid='25da606b-dbd3-45e1-bb23-ff1f84a5622a',
            name='Item 1',
            description='Item 1 description',
            price=5.24,
            availability=10,
            category='scarpe',
        )
        self.item2 = Item.create(
            uuid='08bd8de0-a4ac-459d-956f-cf6d8b8a7507',
            name='Item 2',
            description='Item 2 description',
            price=8,
            availability=10,
            category='scarpe',
        )

    def test_order_json__success(self):
        order = Order.create(
            delivery_address=self.addr, user=self.user,
            uuid='451b3bba-fe4d-470d-bf48-cb306c939bc6',
            created_at=datetime(2017, 5, 1, 9, 4, 47)
        ).add_item(self.item1, 2).add_item(self.item2, 5)

        parsed, _ = OrderSchema.jsonapi(
            order, include_data=['items', 'user', 'delivery_address'])

        assert type(parsed) == str

        expected_result = EXPECTED_ORDERS['order_json__success']
        assert_valid_response(parsed, expected_result)

    def test_order_validate_input__success(self):
        data = {
            "relationships": {
                "user": {
                    "type": "user",
                    "id": "cfe57aa6-76c6-433d-93fe-443363978904"
                },
                "items": [
                    {
                        "type": "item",
                        "id": "25da606b-dbd3-45e1-bb23-ff1f84a5622a",
                        "quantity": 2
                    },
                    {
                        "type": "item",
                        "id": "08bd8de0-a4ac-459d-956f-cf6d8b8a7507",
                        "quantity": 2
                    }
                ],
                "delivery_address": {
                    "type": "address",
                    "id": "27e375f4-3d54-458c-91e4-d8a4fdf3b032"
                }
            }
        }
        post_data = format_jsonapi_request('order', data)
        errors = OrderSchema.validate_input(post_data)
        assert errors == {}

    def test_orders_list__success(self):
        order1 = Order.create(
            delivery_address=self.addr, user=self.user,
            uuid='451b3bba-fe4d-470d-bf48-cb306c939bc6',
            created_at=datetime(2017, 5, 1, 9, 4, 47),
        ).add_item(self.item1)
        order2 = Order.create(
            delivery_address=self.addr, user=self.user,
            uuid='27e375f4-3d54-458c-91e4-d8a4fdf3b032',
            created_at=datetime(2017, 5, 1, 9, 4, 47),
        ).add_item(self.item2, 2)

        parsed = OrderSchema.jsonapi_list([order1, order2])

        assert type(parsed) is str

        expected_result = EXPECTED_ORDERS['get_orders_list__success']
        assert_valid_response(parsed, expected_result)

    def test_order_validate_fields__fail(self):
        order = {
            'relationships': {
                'items': [
                    # Items relationship should not be empty
                ],
                # Missing delivery_address relationship
                # Missing user relationship
            }
        }

        post_data = format_jsonapi_request('order', order)

        errors = OrderSchema.validate_input(post_data)

        expected_result = EXPECTED_ORDERS['order_validate_fields__fail']
        assert_valid_response(errors, expected_result)


class TestAddressSchema(TestCase):
    def setup_method(self):
        super(TestAddressSchema, self).setup_method()
        self.data = {
            'country': 'Italy',
            'city': 'Florence',
            'post_code': '50100',
            'address': 'Via dei matti 0',
            'phone': '0051234567',
            'relationships': {
                'user': {'type': 'user', 'id': '9630b105-ca99-4a27-a51d-ab3430bf52d1'}
            }
        }
        self.user = add_user(email='e@mail.com', password='123',
                             id='9630b105-ca99-4a27-a51d-ab3430bf52d1')
        self.addr = add_address(self.user,
                                id='943d754e-5826-4d5c-b878-47edc478b789')

    def test_address_validate_input__success(self):
        post_data = format_jsonapi_request('address', self.data)
        errors = AddressSchema.validate_input(post_data)

        assert errors == {}

    def test_address_validate_input__fail(self):
        data = copy.deepcopy(self.data)
        data['country'] = ''
        del data['relationships']['user']

        post_data = format_jsonapi_request('address', data)
        errors = AddressSchema.validate_input(post_data)

        expected_result = EXPECTED_ADDRESSES['address_validate_input__fail']
        assert_valid_response(errors, expected_result)

    def test_get_address_json__success(self):

        data, errors = AddressSchema.jsonapi(self.addr)

        assert errors == {}
        assert type(data) is str

        expected_result = EXPECTED_ADDRESSES['get_address_json__success']
        assert_valid_response(data, expected_result)

    def test_address_json_include_user__success(self):
        data, errors = AddressSchema.jsonapi(self.addr, include_data=['user'])

        assert errors == {}
        assert type(data) is str

        expected_result = EXPECTED_ADDRESSES['get_address_json_include_user__success']
        assert_valid_response(data, expected_result)

    def test_get_addresses_list__success(self):
        add_address(
            self.user, id='4373d5d7-cae5-42bc-b218-d6fc6d18626f')

        addr_list = [a for a in Address.select()]
        data = AddressSchema.jsonapi_list(addr_list)

        expected_result = EXPECTED_ADDRESSES['get_addresses_list__success']
        assert_valid_response(data, expected_result)


class TestItemSchema(TestCase):
    def setup_method(self):
        super(TestItemSchema, self).setup_method()
        self.data = {
            'name': 'Test item',
            'price': 10.25,
            'description': 'Test item description',
            'availability': 73,
            'category': 'scarpe',
        }
        self.item1 = Item.create(
            uuid='25da606b-dbd3-45e1-bb23-ff1f84a5622a',
            name='Item 1',
            description='Item 1 description',
            price=5.24,
            availability=5,
            category='scarpe',
        )
        self.item2 = Item.create(
            uuid='08bd8de0-a4ac-459d-956f-cf6d8b8a7507',
            name='Item 2',
            description='Item 2 description',
            price=8,
            availability=10,
            category='accessori',
        )
        self.picture = Picture.create(
            item=self.item1,
            uuid='08bd8de0-a4ac-459d-956f-cf6d8b8a7507',
            extension='png',
        )

    def test_item_validate_input__success(self):
        post_data = format_jsonapi_request('item', self.data)
        errors = ItemSchema.validate_input(post_data)

        assert errors == {}

    def test_item_validate_input__fail(self):
        data = {
            'name': '',          # not empty
            'price': -2,         # more than 0
            'availability': -2,  # more than 0
            'description': '',   # not empty
            'category': '',      # not empty
        }
        post_data = format_jsonapi_request('item', data)
        errors = ItemSchema.validate_input(post_data)

        expected_result = EXPECTED_ITEMS['item_validate_input__fail']
        assert_valid_response(errors, expected_result)

    def test_get_item_json__success(self):
        data, errors = ItemSchema.jsonapi(self.item1)

        assert errors == {}
        expected_result = EXPECTED_ITEMS['get_item_json__success']
        assert_valid_response(data, expected_result)

    def test_get_items_list__success(self):
        data = ItemSchema.jsonapi_list([self.item1, self.item2])
        expected_result = EXPECTED_ITEMS['get_items_list__success']
        assert_valid_response(data, expected_result)

    def test_get_item_include_pictures__success(self):
        data, errors = ItemSchema.jsonapi(
            self.item1, include_data=['pictures'])

        assert errors == {}
        expected_result = EXPECTED_ITEMS['get_item_include_pictures__success']
        assert_valid_response(data, expected_result)


class TestPictureSchema(TestCase):
    @classmethod
    def setup_class(cls):
        super(TestPictureSchema, cls).setup_class()
        utils.get_image_folder = lambda: TEST_IMAGE_FOLDER
        test_utils.get_image_folder = utils.get_image_folder

    def setup_method(self):
        super(TestPictureSchema, self).setup_method()
        self.item = Item.create(
            uuid='25da606b-dbd3-45e1-bb23-ff1f84a5622a',
            name='Item 1',
            description='Item 1 description',
            price=5.24,
            availability=5,
            category='scarpe',
        )
        self.picture = Picture.create(
            item=self.item,
            uuid='08bd8de0-a4ac-459d-956f-cf6d8b8a7507',
            extension='png',
        )

    def test_get_picture_json__success(self):
        data, _ = PictureSchema.jsonapi(self.picture)
        expected_result = EXPECTED_PICTURES['get_picture_json__success']
        assert_valid_response(data, expected_result)
