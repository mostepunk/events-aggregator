# Events Aggregator — Витрина навыков MongoDB

## Цели проекта
- Продемонстрировать глубокое владение MongoDB: моделирование данных, индексация, агрегации, вложенные документы, транзакции, TTL, поиск, оптимизация и интеграция с Python/FastAPI
- Создать продуктивный pet-проект для портфолио с чистой event-driven архитектурой
- Реализовать централизованный сервис сбора и анализа событий

---

## 1. Описание проекта
**Events Aggregator** — микросервис для централизованного сбора, хранения, анализа и обработки событий от различных источников в распределенной системе.

### Основные функции:
- **Сбор событий** из message broker от различных микросервисов
- **Применение правил** для обработки критичных событий
- **Аналитика и отчетность** на основе собранных данных
- **REST API** для просмотра событий и метрик
- **Real-time мониторинг** через WebSocket/SSE

---

## 2. Архитектура системы

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SYSTEMS                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Auth        │  │ Payment     │  │ Order       │  │ User        │             │
│  │ Service     │  │ Service     │  │ Service     │  │ Service     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                │                │                │                    │
│         ▼                ▼                ▼                ▼                    │
│  ┌─────────────────────────────────────────────────────────────┐                │
│  │                 Message Broker                              │                │
│  │        (Redis Pub/Sub / RabbitMQ / Kafka)                   │                │
│  │                                                             │                │
│  │  Topics:                                                    │                │
│  │  • events.user.login      • events.payment.failed           │                │
│  │  • events.system.error    • events.order.created            │                │
│  │  • events.notification.delivery                             │                │
│  └─────────────────────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          EVENTS AGGREGATOR                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐                                 ┌─────────────────┐        │
│  │  Event Consumer │                                 │  REST API       │        │
│  │                 │                                 │                 │        │
│  │  • Consumes     │                                 │  GET /events    │        │
│  │    events       │                                 │  GET /analytics │        │
│  │  • Validates    │                                 │  GET /metrics   │        │
│  │  • Enriches     │                                 │  GET /rules     │        │
│  │  • Bulk writes  │                                 │  POST /rules    │        │
│  └─────────────────┘                                 │  GET /stream    │        │
│           │                                          └─────────────────┘        │
│           ▼                                                   │                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                      BUSINESS LOGIC LAYER                                   ││
│  │                                                                             ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         ││
│  │  │Event        │  │Rules        │  │Analytics    │  │Stream       │         ││
│  │  │Processor    │  │Engine       │  │Engine       │  │Service      │         ││
│  │  │             │  │             │  │             │  │             │         ││
│  │  │• Validation │  │• Rule       │  │• Aggregation│  │• Change     │         ││
│  │  │• Enrichment │  │  matching   │  │• Reports    │  │  Streams    │         ││
│  │  │• Storage    │  │• Actions    │  │• Metrics    │  │• WebSocket  │         ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│           │                    │                    │                    │      │
│           ▼                    ▼                    ▼                    ▼      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                         MONGODB CLUSTER                                     ││
│  │                                                                             ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         ││
│  │  │   events    │  │    rules    │  │   metrics   │  │    users    │         ││
│  │  │             │  │             │  │             │  │             │         ││
│  │  │• Flexible   │  │• Conditions │  │• Aggregated │  │• Minimal    │         ││
│  │  │  schema     │  │• Actions    │  │  data       │  │  profile    │         ││
│  │  │• TTL index  │  │• Priorities │  │• Time-based │  │• Preferences│         ││
│  │  │• Text search│  │             │  │• Cached     │  │             │         ││
│  │  │• Compound   │  │             │  │  results    │  │             │         ││
│  │  │  indexes    │  │             │  │             │  │             │         ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                    │                                            │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT ACTIONS                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │Notification │  │   Webhook   │  │   Logging   │  │   Alerting  │             │
│  │   Queue     │  │  Triggers   │  │  Service    │  │   System    │             │
│  │             │  │             │  │             │  │             │             │
│  │• Critical   │  │• External   │  │• Structured │  │• Monitoring │             │
│  │  events     │  │  systems    │  │  logs       │  │• Dashboards │             │
│  │• Retry      │  │• Callbacks  │  │• Audit      │  │• Metrics    │             │
│  │  logic      │  │             │  │  trail      │  │  export     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Структура данных MongoDB

### 3.1 Коллекция `events`
```javascript
{
  "_id": ObjectId,
  "event_id": "uuid-v4",
  "type": "USER_LOGIN | PAYMENT_FAILED | SYSTEM_ERROR | ORDER_CREATED",
  "source": "auth-service",
  "severity": 1-10,  // 1-3: info, 4-6: warning, 7-8: error, 9-10: critical
  "timestamp": ISODate,
  "user_id": "string",
  "session_id": "string",
  "trace_id": "string",
  "payload": {
    // Гибкая структура в зависимости от типа события
    "user_email": "user@example.com",
    "amount": 1000,
    "currency": "USD",
    "error_code": "PAYMENT_DECLINED"
  },
  "metadata": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "region": "US-EAST-1",
    "version": "1.0.0"
  },
  "processed": true,
  "created_at": ISODate,
  "expires_at": ISODate  // TTL
}
```

### 3.2 Коллекция `rules`
```javascript
{
  "_id": ObjectId,
  "name": "Critical Payment Failures",
  "description": "Notify on multiple payment failures",
  "conditions": {
    "type": "PAYMENT_FAILED",
    "severity": {"$gte": 7},
    "payload.amount": {"$gte": 1000}
  },
  "actions": [
    {
      "type": "SEND_NOTIFICATION",
      "config": {
        "queue": "notifications.critical",
        "template": "payment_failure_alert",
        "recipients": ["admin@company.com"]
      }
    },
    {
      "type": "WEBHOOK",
      "config": {
        "url": "https://monitoring.company.com/webhooks",
        "method": "POST",
        "headers": {"Authorization": "Bearer token"}
      }
    }
  ],
  "priority": 1,
  "enabled": true,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 3.3 Коллекция `metrics`
```javascript
{
  "_id": ObjectId,
  "metric_type": "EVENTS_COUNT | ERROR_RATE | RESPONSE_TIME",
  "dimensions": {
    "event_type": "PAYMENT_FAILED",
    "source": "payment-service",
    "region": "US-EAST-1"
  },
  "value": 150,
  "timestamp": ISODate,
  "period": "1h",  // 1m, 5m, 1h, 1d
  "created_at": ISODate,
  "expires_at": ISODate  // TTL
}
```

### 3.4 Коллекция `users`
```javascript
{
  "_id": ObjectId,
  "user_id": "string",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin | user",
  "preferences": {
    "notification_channels": ["email", "sms"],
    "event_types": ["CRITICAL_ERROR", "PAYMENT_FAILED"]
  },
  "created_at": ISODate,
  "updated_at": ISODate
}
```

---

## 4. MongoDB возможности в проекте

### 4.1 Индексы
```javascript
// Основные индексы
db.events.createIndex({ "type": 1, "timestamp": -1, "severity": -1 })
db.events.createIndex({ "user_id": 1, "timestamp": -1 })
db.events.createIndex({ "source": 1, "timestamp": -1 })
db.events.createIndex({ "trace_id": 1 })
db.events.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })  // TTL

// Текстовый поиск
db.events.createIndex({ 
  "payload": "text", 
  "metadata": "text" 
})

// Геоиндекс (если нужна геолокация)
db.events.createIndex({ "metadata.location": "2dsphere" })
```

### 4.2 Агрегации
```javascript
// Пример: события по типам за последние 24 часа
db.events.aggregate([
  {
    $match: {
      timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
    }
  },
  {
    $group: {
      _id: "$type",
      count: { $sum: 1 },
      avg_severity: { $avg: "$severity" }
    }
  },
  {
    $sort: { count: -1 }
  }
])
```

### 4.3 Change Streams
```javascript
// Мониторинг критичных событий в реальном времени
db.events.watch([
  {
    $match: {
      "fullDocument.severity": { $gte: 8 }
    }
  }
])
```

### 4.4 Транзакции
```javascript
// Атомарная обработка правила и создание уведомления
session.withTransaction(async () => {
  await events.updateOne(
    { _id: eventId },
    { $set: { processed: true } }
  )
  
  await notifications.insertOne({
    event_id: eventId,
    status: "pending",
    created_at: new Date()
  })
})
```

---

## 5. REST API

### 5.1 Events
- `GET /api/v1/events` - получить события с фильтрацией
- `GET /api/v1/events/{event_id}` - получить конкретное событие
- `POST /api/v1/events` - создать событие (для тестирования)
- `GET /api/v1/events/search` - текстовый поиск по событиям

### 5.2 Analytics
- `GET /api/v1/analytics/summary` - общая статистика
- `GET /api/v1/analytics/trends` - тренды по времени
- `GET /api/v1/analytics/top-errors` - топ ошибок
- `GET /api/v1/analytics/user-activity` - активность пользователей

### 5.3 Rules
- `GET /api/v1/rules` - получить все правила
- `POST /api/v1/rules` - создать правило
- `PUT /api/v1/rules/{rule_id}` - обновить правило
- `DELETE /api/v1/rules/{rule_id}` - удалить правило

### 5.4 Real-time
- `GET /api/v1/stream/events` - SSE поток событий
- `GET /api/v1/stream/metrics` - SSE поток метрик
- `WebSocket /ws/events` - WebSocket для real-time обновлений

---

## 6. Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - web framework
- **pymongo** - MongoDB driver
- **motor** - async MongoDB driver
- **pydantic** - data validation
- **celery** - background tasks
- **redis** - message broker & cache

### Database
- **MongoDB 6.0+**
- **Redis 7.0+** - для брокера сообщений

---

## 7. Запуск проекта
Work in progress

---

## 8. Мониторинг и метрики

### 8.1 Healthcheck endpoints
- `GET /health` - статус сервиса
- `GET /health/mongodb` - состояние MongoDB
- `GET /health/redis` - состояние Redis

### 8.2 Prometheus метрики (???)
- `events_total` - общее количество событий
- `events_processed_duration` - время обработки
- `rules_matched_total` - количество сработавших правил
- `mongodb_operations_total` - операции с БД

---

## 9. Что демонстрирует проект

### MongoDB навыки:
- ✅ Гибкое моделирование данных (schema-less)
- ✅ Составные и текстовые индексы
- ✅ Агрегационные pipeline
- ✅ TTL для автоматического удаления данных
- ✅ Change Streams для real-time обновлений
- ✅ Транзакции для атомарных операций
- ✅ Bulk операции для производительности
- ✅ Поиск по тексту и геоданным
- ✅ Оптимизация запросов

### Архитектурные решения:
- ✅ Event-driven архитектура
- ✅ Микросервисная архитектура
- ✅ Асинхронная обработка
- ✅ Масштабируемость
- ✅ Мониторинг и логирование

---

## 10. Дальнейшее развитие

### Возможные улучшения:
- **Шардинг** MongoDB для горизонтального масштабирования
- **Machine Learning** для анализа аномалий в событиях
- **GraphQL** API для более гибких запросов
- **Kafka** для более надежной обработки событий
- **Kubernetes** для оркестрации в production
