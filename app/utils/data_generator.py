import json
import random
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Generator, Optional

from app.utils.fake_client import fake


@dataclass(frozen=True, slots=True)
class EventTemplate:
    """Шаблон для генерации событий определенного типа"""

    event_type: str
    source: str
    severity_range: tuple[int, int]
    # Вес для случайного выбора (чем больше, тем чаще)
    weight: float


class EventDataGenerator:
    """Генератор тестовых данных для Events Aggregator

    Примеры использования:

    # Для воспроизводимых результатов
    generator = EventDataGenerator(seed=42)

    # Генерация 100 событий
    generator = EventDataGenerator()
    events: list[dict] = list(generator(100))

    # Генерация только критичных событий
    critical_events: list[dict] = list(generator(50, severity_filter=(8, 10)))
    """

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            fake.seed_instance(seed)

        self.users = [fake.user() for _ in range(50)]
        self.products = [fake.product() for _ in range(100)]
        # fmt: off
        # Шаблоны событий с весами (чем больше вес, тем чаще генерируется)
        self.event_templates = [
            EventTemplate("USER_LOGIN_SUCCESS", "auth-service", (1, 3), 30.0),
            EventTemplate("USER_LOGIN_FAILED", "auth-service", (4, 8), 5.0),
            EventTemplate("USER_REGISTERED", "auth-service", (2, 3), 3.0),
            EventTemplate("PAYMENT_SUCCESS", "payment-service", (1, 3), 20.0),
            EventTemplate("PAYMENT_FAILED", "payment-service", (6, 9), 8.0),
            EventTemplate("PAYMENT_REFUNDED", "payment-service", (3, 5), 2.0),
            EventTemplate("ORDER_CREATED", "order-service", (1, 3), 25.0),
            EventTemplate("ORDER_CANCELLED", "order-service", (4, 6), 4.0),
            EventTemplate("SYSTEM_ERROR", "payment-service", (7, 10), 1.0),
            EventTemplate("RATE_LIMIT_EXCEEDED", "api-gateway", (5, 7), 2.0),
            EventTemplate("NOTIFICATION_DELIVERED", "notification-service", (1, 3), 15.0),
            EventTemplate("NOTIFICATION_FAILED", "notification-service", (5, 8), 3.0),
            EventTemplate("USER_PROFILE_UPDATED", "user-service", (1, 3), 5.0),
            EventTemplate("AB_TEST_CONVERSION", "analytics-service", (2, 4), 2.0),
        ]
        # fmt: on

    def _get_random_user(self) -> dict:
        """Возвращает случайного пользователя"""
        return random.choice(self.users)

    def _generate_base_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует базовую структуру события"""
        return {
            "event_id": str(uuid.uuid4()),
            "type": template.event_type,
            "source": template.source,
            "severity": random.randint(*template.severity_range),
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "user_id": user["user_id"] if user else None,
            "session_id": f"sess_{fake.uuid4()[:12]}" if user else None,
            "trace_id": f"trace_{fake.uuid4()[:8]}",
        }

    def _generate_auth_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует события аутентификации"""
        event = self._generate_base_event(template, user)

        if template.event_type == "USER_LOGIN_SUCCESS":
            event["payload"] = {
                "email": user["email"],
                "login_method": random.choice(
                    ["password", "oauth_google", "oauth_facebook"]
                ),
                "remember_me": random.choice([True, False]),
                "device_fingerprint": f"fp_{fake.uuid4()[:8]}",
                "two_factor_used": random.choice([True, False]),
            }

        elif template.event_type == "USER_LOGIN_FAILED":
            event["payload"] = {
                "email": user["email"],
                "failure_reason": random.choice(
                    [
                        "invalid_password",
                        "invalid_email",
                        "account_locked",
                        "suspicious_activity",
                    ]
                ),
                "attempt_number": random.randint(1, 10),
                "account_locked": random.choice([True, False]),
                "lock_duration_minutes": random.choice([15, 30, 60, 120]),
                "suspicious_activity": event["severity"] >= 7,
            }

        elif template.event_type == "USER_REGISTERED":
            event["payload"] = {
                "email": user["email"],
                "registration_method": random.choice(
                    ["email", "oauth_google", "oauth_facebook"]
                ),
                "email_verified": random.choice([True, False]),
                "profile_completed": random.choice([True, False]),
                "referral_code": (
                    f"REF{random.randint(100, 999)}" if random.random() > 0.7 else None
                ),
                "marketing_consent": random.choice([True, False]),
                "terms_version": "v2.1",
                "account_type": random.choice(["free", "premium"]),
            }

        # Общие метаданные для auth событий
        event["metadata"] = {
            "ip_address": fake.ipv4(),
            "user_agent": fake.user_agent(),
            "country": user["country"],
            "city": user["city"],
            "device_type": random.choice(["desktop", "mobile", "tablet"]),
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
            "version": f"{template.source}-v{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    def _generate_payment_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует события платежей"""
        event = self._generate_base_event(template, user)

        amount = round(random.uniform(9.99, 1999.99), 2)
        order_id = f"order_{random.randint(100000, 999999)}"

        if template.event_type == "PAYMENT_SUCCESS":
            event["payload"] = {
                "transaction_id": f"txn_{fake.uuid4()[:12]}",
                "order_id": order_id,
                "amount": amount,
                "currency": random.choice(["USD", "EUR", "RUB"]),
                "payment_method": random.choice(
                    ["credit_card", "debit_card", "cash", "apple_pay"]
                ),
                "card_last_four": str(random.randint(1000, 9999)),
                "card_brand": random.choice(["visa", "mastercard", "amex"]),
                "processor": random.choice(["stripe", "paypal", "square"]),
                "processor_transaction_id": f"pi_{fake.uuid4()[:12]}",
                "merchant_fee": round(amount * 0.029 + 0.30, 2),
                "net_amount": round(amount - (amount * 0.029 + 0.30), 2),
                "processing_time_ms": random.randint(500, 3000),
            }

        elif template.event_type == "PAYMENT_FAILED":
            event["payload"] = {
                "transaction_id": f"txn_failed_{fake.uuid4()[:8]}",
                "order_id": order_id,
                "amount": amount,
                "currency": "USD",
                "payment_method": "credit_card",
                "card_last_four": str(random.randint(1000, 9999)),
                "card_brand": random.choice(["visa", "mastercard", "amex"]),
                "processor": "stripe",
                "failure_code": random.choice(
                    [
                        "insufficient_funds",
                        "card_declined",
                        "expired_card",
                        "cvc_check_failed",
                    ]
                ),
                "failure_message": "Your card was declined",
                "retry_attempt": random.randint(1, 3),
                "max_retries": 3,
                "final_failure": random.choice([True, False]),
            }

        elif template.event_type == "PAYMENT_REFUNDED":
            event["payload"] = {
                "refund_id": f"ref_{fake.uuid4()[:12]}",
                "original_transaction_id": f"txn_{fake.uuid4()[:12]}",
                "original_order_id": order_id,
                "refund_amount": amount,
                "refund_reason": random.choice(
                    [
                        "customer_request",
                        "item_not_received",
                        "item_damaged",
                        "wrong_item",
                    ]
                ),
                "refund_type": random.choice(["full", "partial"]),
                "initiated_by": random.choice(
                    ["customer", "customer_service", "system"]
                ),
                "agent_id": (
                    f"agent_{random.randint(100, 999)}"
                    if random.random() > 0.5
                    else None
                ),
                "processing_time_days": random.randint(1, 7),
                "refund_method": "original_payment_method",
            }

        event["metadata"] = {
            "ip_address": fake.ipv4(),
            "country": user["country"],
            "processor_response_code": (
                "approved" if "SUCCESS" in template.event_type else "declined"
            ),
            "risk_score": round(random.uniform(0.1, 9.9), 1),
            "version": f"{template.source}-v{random.randint(1,2)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    def _generate_order_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует события заказов"""
        event = self._generate_base_event(template, user)

        # Выбираем случайные продукты
        selected_products = random.sample(self.products, random.randint(1, 3))
        total_amount = sum(p["price"] * random.randint(1, 3) for p in selected_products)

        if template.event_type == "ORDER_CREATED":
            items = []
            for product in selected_products:
                quantity = random.randint(1, 3)
                items.append(
                    {
                        "product_id": product["id"],
                        "name": product["name"],
                        "quantity": quantity,
                        "price": product["price"],
                        "category": product["category"],
                    }
                )

            event["payload"] = {
                "order_id": f"order_{random.randint(100000, 999999)}",
                "total_amount": round(total_amount, 2),
                "currency": "USD",
                "item_count": len(items),
                "items": items,
                "shipping_address": {
                    "country": user["country"],
                    "state": fake.state_abbr(),
                    "city": user["city"],
                    "zip": fake.zipcode(),
                },
                "shipping_method": random.choice(["standard", "express", "overnight"]),
                "estimated_delivery": (
                    datetime.now(UTC) + timedelta(days=random.randint(2, 10))
                ).isoformat()
                + "Z",
            }

        elif template.event_type == "ORDER_CANCELLED":
            event["payload"] = {
                "order_id": f"order_{random.randint(100000, 999999)}",
                "cancellation_reason": random.choice(
                    [
                        "customer_request",
                        "payment_failed",
                        "out_of_stock",
                        "address_issue",
                    ]
                ),
                "cancelled_by": random.choice(["customer", "system", "admin"]),
                "refund_initiated": random.choice([True, False]),
                "restocking_required": True,
                "items_to_restock": [
                    {"product_id": p["id"], "quantity": random.randint(1, 3)}
                    for p in selected_products
                ],
            }

        event["metadata"] = {
            "cart_session_duration_minutes": random.randint(5, 120),
            "utm_source": random.choice(["google", "facebook", "email", "direct"]),
            "utm_campaign": random.choice(
                ["summer_sale", "black_friday", "new_year", None]
            ),
            "version": f"{template.source}-v{random.randint(2,4)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    def _generate_system_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует системные события"""
        event = self._generate_base_event(
            template, None
        )  # Системные события без пользователя

        if template.event_type == "SYSTEM_ERROR":
            event["payload"] = {
                "error_type": random.choice(
                    [
                        "database_connection_failed",
                        "external_api_timeout",
                        "memory_exceeded",
                        "disk_full",
                    ]
                ),
                "error_message": random.choice(
                    [
                        "Connection to primary database lost",
                        "External payment API timeout",
                        "Memory usage exceeded 90%",
                        "Disk space critically low",
                    ]
                ),
                "error_code": random.choice(
                    [
                        "DB_CONNECTION_TIMEOUT",
                        "API_TIMEOUT",
                        "MEMORY_EXCEEDED",
                        "DISK_FULL",
                    ]
                ),
                "stack_trace": "Exception in thread main...",
                "affected_endpoints": random.sample(
                    ["/api/v1/payments", "/api/v1/orders", "/api/v1/users"],
                    random.randint(1, 3),
                ),
                "estimated_affected_users": random.randint(100, 5000),
                "fallback_activated": random.choice([True, False]),
                "fallback_type": random.choice(
                    ["read_replica", "cache", "degraded_mode"]
                ),
            }

        elif template.event_type == "RATE_LIMIT_EXCEEDED":
            event["user_id"] = user["user_id"] if user else f"user_{fake.uuid4()[:8]}"
            event["payload"] = {
                "endpoint": random.choice(
                    ["/api/v1/orders", "/api/v1/payments", "/api/v1/users"]
                ),
                "method": random.choice(["GET", "POST", "PUT"]),
                "rate_limit": random.choice([100, 1000, 5000]),
                "time_window": random.choice(["1m", "1h", "1d"]),
                "current_count": random.randint(150, 2000),
                "client_ip": fake.ipv4(),
                "client_id": f"client_{fake.uuid4()[:8]}",
                "blocked_duration_seconds": random.choice([60, 300, 3600]),
            }

        event["metadata"] = {
            "service_instance": f"{template.source}-pod-{random.randint(1, 10)}",
            "kubernetes_namespace": "production",
            "version": f"{template.source}-v{random.randint(1,2)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    def _generate_notification_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует события уведомлений"""
        event = self._generate_base_event(template, user)

        if template.event_type == "NOTIFICATION_DELIVERED":
            event["payload"] = {
                "notification_id": f"notif_{random.choice(['email', 'sms', 'push'])}_{fake.uuid4()[:8]}",
                "channel": random.choice(["email", "sms", "push"]),
                "template": random.choice(
                    [
                        "payment_failure_alert",
                        "order_confirmation",
                        "welcome_email",
                        "password_reset",
                    ]
                ),
                "recipient": (
                    user["email"] if random.random() > 0.5 else fake.phone_number()
                ),
                "subject": fake.sentence()[:50],
                "triggered_by_event": str(uuid.uuid4()),
                "delivery_time_ms": random.randint(1000, 5000),
                "provider": random.choice(["sendgrid", "twilio", "firebase"]),
                "provider_message_id": f"msg_{fake.uuid4()[:12]}",
            }

        elif template.event_type == "NOTIFICATION_FAILED":
            event["payload"] = {
                "notification_id": f"notif_{random.choice(['email', 'sms', 'push'])}_{fake.uuid4()[:8]}",
                "channel": random.choice(["email", "sms", "push"]),
                "template": random.choice(
                    ["payment_failure_alert", "order_confirmation"]
                ),
                "recipient": (
                    user["email"] if random.random() > 0.5 else fake.phone_number()
                ),
                "message": fake.sentence(),
                "triggered_by_event": str(uuid.uuid4()),
                "failure_reason": random.choice(
                    [
                        "invalid_email",
                        "invalid_phone_number",
                        "provider_error",
                        "rate_limited",
                    ]
                ),
                "provider_error_code": str(random.randint(20000, 29999)),
                "retry_attempt": random.randint(1, 3),
                "max_retries": 3,
                "next_retry_at": (
                    datetime.now(UTC) + timedelta(minutes=random.randint(5, 60))
                ).isoformat()
                + "Z",
                "provider": random.choice(["sendgrid", "twilio", "firebase"]),
            }

        event["metadata"] = {
            "cost_usd": round(random.uniform(0.001, 0.05), 4),
            "version": f"{template.source}-v{random.randint(1,2)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    def _generate_user_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует пользовательские события"""
        event = self._generate_base_event(template, user)

        if template.event_type == "USER_PROFILE_UPDATED":
            updated_fields = random.sample(
                ["phone", "address", "preferences", "name"], random.randint(1, 3)
            )
            event["payload"] = {
                "updated_fields": updated_fields,
                "changes": {
                    field: {
                        "old": (
                            fake.phone_number() if field == "phone" else fake.address()
                        ),
                        "new": (
                            fake.phone_number() if field == "phone" else fake.address()
                        ),
                    }
                    for field in updated_fields
                },
                "verification_required": [
                    field for field in updated_fields if field in ["phone", "email"]
                ],
                "gdpr_consent_updated": random.choice([True, False]),
            }

        event["metadata"] = {
            "ip_address": fake.ipv4(),
            "user_agent": fake.user_agent(),
            "version": f"{template.source}-v{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    def _generate_analytics_event(self, template: EventTemplate, user: dict) -> dict:
        """Генерирует аналитические события"""
        event = self._generate_base_event(template, user)

        if template.event_type == "AB_TEST_CONVERSION":
            event["payload"] = {
                "experiment_id": random.choice(
                    ["checkout_flow_v2", "homepage_hero", "pricing_page", "signup_form"]
                ),
                "variant": random.choice(["control", "treatment_a", "treatment_b"]),
                "conversion_event": random.choice(
                    ["purchase_completed", "signup_completed", "trial_started"]
                ),
                "conversion_value": round(random.uniform(10, 500), 2),
                "time_to_conversion_minutes": random.randint(1, 120),
                "user_segment": random.choice(
                    ["new_user", "returning_customer", "premium_user"]
                ),
                "previous_conversions": random.randint(0, 10),
            }

        event["metadata"] = {
            "experiment_start_date": (
                datetime.now(UTC) - timedelta(days=random.randint(1, 30))
            ).isoformat()
            + "Z",
            "confidence_level": random.choice([90, 95, 99]),
            "statistical_significance": random.choice([True, False]),
            "version": f"{template.source}-v{random.randint(1,2)}.{random.randint(0,9)}.{random.randint(0,9)}",
        }

        return event

    # TODO: отрефакторить метод
    def generate_event(self, severity_filter: Optional[tuple[int, int]] = None) -> dict:
        """Генерирует одно случайное событие

        Args:
            severity_filter: Фильтр по severity (min, max)
        """
        # Если задан фильтр severity, отбираем только подходящие шаблоны
        if severity_filter:
            # Фильтруем шаблоны, у которых диапазоны пересекаются с фильтром
            suitable_templates = []
            suitable_weights = []

            for template in self.event_templates:
                # Проверяем пересечение диапазонов
                min_severity = max(template.severity_range[0], severity_filter[0])
                max_severity = min(template.severity_range[1], severity_filter[1])

                if min_severity <= max_severity:  # Диапазоны пересекаются
                    suitable_templates.append(template)
                    suitable_weights.append(template.weight)

            if not suitable_templates:
                raise ValueError(
                    f"Нет событий с severity в диапазоне {severity_filter}"
                )

            # Выбираем шаблон из подходящих
            template = random.choices(suitable_templates, weights=suitable_weights)[0]

            # Генерируем severity в пересечении диапазонов
            min_severity = max(template.severity_range[0], severity_filter[0])
            max_severity = min(template.severity_range[1], severity_filter[1])
            severity = random.randint(min_severity, max_severity)

            # Создаем копию шаблона с новым severity
            template = EventTemplate(
                template.event_type,
                template.source,
                (severity, severity),
                template.weight,
            )
        else:
            # Выбираем шаблон события на основе весов (без фильтра)
            weights = [t.weight for t in self.event_templates]
            template = random.choices(self.event_templates, weights=weights)[0]

        # Выбираем пользователя (или None для системных событий)
        user = (
            self._get_random_user()
            if template.event_type not in ["SYSTEM_ERROR"]
            else None
        )

        # Генерируем событие в зависимости от типа
        if template.source == "auth-service":
            return self._generate_auth_event(template, user)
        elif template.source == "payment-service" and template.event_type.startswith(
            "PAYMENT"
        ):
            return self._generate_payment_event(template, user)
        elif template.source == "order-service":
            return self._generate_order_event(template, user)
        elif template.event_type in ["SYSTEM_ERROR", "RATE_LIMIT_EXCEEDED"]:
            return self._generate_system_event(template, user)
        elif template.source == "notification-service":
            return self._generate_notification_event(template, user)
        elif template.source == "user-service":
            return self._generate_user_event(template, user)
        elif template.source == "analytics-service":
            return self._generate_analytics_event(template, user)
        else:
            return self._generate_base_event(template, user)

    def __call__(
        self, count: int, severity_filter: Optional[tuple[int, int]] = None
    ) -> Generator[dict, None, None]:
        """Генерирует батч событий

        Args:
            count: Количество событий
            severity_filter: Фильтр по severity (min, max)
        """
        for _ in range(count):
            yield self.generate_event(severity_filter)

    def save_to_file(self, events: list[dict], filename: str, format: str = "json"):
        """Сохраняет события в файл

        Args:
            events: Список событий
            filename: Имя файла
            format: Формат файла (json, jsonl)
        """
        if format == "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
        elif format == "jsonl":
            with open(filename, "w", encoding="utf-8") as f:
                for event in events:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def print_statistics(self, events: list[dict]):
        """Выводит статистику по сгенерированным событиям"""
        print(f"\n📊 Статистика сгенерированных событий:")
        print(f"Всего событий: {len(events)}")

        # Группировка по типам
        type_counts = {}
        severity_counts = {}
        source_counts = {}

        for event in events:
            event_type = event["type"]
            severity = event["severity"]
            source = event["source"]

            type_counts[event_type] = type_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1

        print("\n📋 По типам событий:")
        for event_type, count in sorted(type_counts.items()):
            print(f"  {event_type}: {count}")

        print("\n⚠️ По уровню серьезности:")
        for severity in sorted(severity_counts.keys()):
            print(f"  Severity {severity}: {severity_counts[severity]}")

        print("\n🔧 По источникам:")
        for source, count in sorted(source_counts.items()):
            print(f"  {source}: {count}")


# Usecases:
# 1. рандомные события
def random_event_data(batch_size: int = 100) -> Generator[dict, None, None]:
    """Генерирует события

    Args:
        batch_size: Количество событий
    """
    event_generator = EventDataGenerator()
    for event in event_generator(batch_size):
        yield event


# 2. информационные события
def generate_info_events(batch_size: int = 100) -> Generator[dict, None, None]:
    """Генерирует информационные события"""
    event_generator = EventDataGenerator()
    for event in event_generator(batch_size, severity_filter=(1, 4)):
        yield event


# 3. критические события
def generate_critical_events(batch_size: int = 100) -> Generator[dict, None, None]:
    """Генерирует критические события"""
    event_generator = EventDataGenerator()
    for event in event_generator(batch_size, severity_filter=(7, 10)):
        yield event


# 4. поток событий
def stream_events(
    time_sleep: float = 1.0, max_events: int = 1000
) -> Generator[dict, None, None]:
    """Генерирует поток событий

    Args:
        time_sleep: Интервал между событиями
        max_events: Максимальное количество событий
    """
    event_generator = EventDataGenerator()
    count = 0

    try:
        while max_events > count:
            count += 1
            yield event_generator.generate_event()
            time.sleep(time_sleep)
    except KeyboardInterrupt:
        print(f"\n Остановлено пользователем. Сгенерировано событий: {count}")
