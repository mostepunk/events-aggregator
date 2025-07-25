import random

from bson.objectid import ObjectId
from faker import Faker
from faker.providers import BaseProvider

# fake = Faker("ru_RU")
fake = Faker()


class IDProvider(BaseProvider):
    def short_id(self) -> str:
        return fake.uuid4()[:8]

    def long_id(self) -> str:
        return fake.uuid4()[:12]

    def mongo_id(self) -> ObjectId:
        return ObjectId()


class UserPorvider(BaseProvider):
    def user(self) -> dict:
        """Генерирует список пользователей для использования в событиях"""
        return {
            "user_id": f"user_{fake.short_id()}",
            "email": fake.email(),
            "name": fake.name(),
            "country": fake.country_code(),
            "city": fake.city(),
        }


class ProductProvider(BaseProvider):
    def category(self) -> dict:
        """Генерирует список пользователей для использования в событиях"""
        return random.choice(["electronics", "accessories", "clothing", "books"])

    def product_name(self) -> dict:
        """Генерирует список пользователей для использования в событиях"""
        return random.choice(
            [
                "Smartphone",
                "Wireless Headphones",
                "Phone Case",
                "Laptop Stand",
                "Bluetooth Speaker",
                "USB-C Cable",
                "Mechanical Keyboard",
            ]
        )

    def product(self) -> dict:
        return {
            "id": f"product_{fake.short_id()}",
            "name": self.product_name(),
            "price": fake.random_int(0, 1000),
            "category": self.category(),
        }


fake.add_provider(IDProvider)
fake.add_provider(UserPorvider)
fake.add_provider(ProductProvider)
