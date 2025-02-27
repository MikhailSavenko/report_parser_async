# Парсер результатов торгов СПбМТСБ

## Описание проекта

Этот проект создан для практики работы с асинхронным кодом и библиотекой `asyncio`. Используется `BeautifulSoup4` для парсинга бюллетеней с результатами торгов с сайта СПбМТСБ, начиная с 2023 года (по умолчанию). Год давности файлов можно изменить с помощью `argparse`. Полученные данные обрабатываются и сохраняются в базу данных для последующего анализа.

Парсер извлекает из таблицы бюллетеня только данные с единицей измерения "Метрическая тонна", где в столбце "Количество Договоров, шт." значение больше 0.

## Используемые технологии и библиотеки

- `beautifulsoup4==4.13.3`
- `aiohttp==3.11.12`
- `xlrd==2.0.1`
- `pandas==2.2.3`
- `sqlalchemy==2.0.38`
- `asyncpg==0.30.0`
- `python-dotenv==1.0.1`
- `lxml==5.3.1`
- `requests==2.32.3`
- `psycopg2-binary==2.9.10`
- `isort==6.0.1`
- `black==25.1.0`
- `flake8==7.1.2`

## Функциональность парсера

Парсер поддерживает два режима работы:

- **Синхронный** – выполняется в стандартном последовательном режиме.
- **Асинхронный** – использует корутины, асинхронную очередь, событийный цикл и отдельный поток для парсинга файлов.

В качестве базы данных используется **PostgreSQL** (поддерживаются драйверы для синхронной и асинхронной работы). Для работы с БД применяется `SQLAlchemy`.

### Основные возможности

- Скачивание бюллетеней торгов с сайта СПбМТСБ.
- Извлечение данных из таблицы "Единица измерения: Метрическая тонна", где "Количество Договоров, шт." > 0.
- Обработка и сохранение следующих столбцов:
  - `exchange_product_id` (Код Инструмента)
  - `exchange_product_name` (Наименование Инструмента)
  - `delivery_basis_name` (Базис поставки)
  - `volume` (Объем Договоров в единицах измерения)
  - `total` (Объем Договоров, руб.)
  - `count` (Количество Договоров, шт.)

### Структура базы данных (`spimex_trading_results`)

| Поле                    | Описание                                  |
| ----------------------- | ----------------------------------------- |
| `id`                    | Уникальный идентификатор записи           |
| `exchange_product_id`   | Код инструмента                           |
| `exchange_product_name` | Наименование инструмента                  |
| `oil_id`                | Первые 4 символа `exchange_product_id`    |
| `delivery_basis_id`     | Символы с 5 по 7 `exchange_product_id`    |
| `delivery_basis_name`   | Базис поставки                            |
| `delivery_type_id`      | Последний символ `exchange_product_id`    |
| `volume`                | Объем договоров в единицах измерения      |
| `total`                 | Общая сумма договоров (руб.)              |
| `count`                 | Количество договоров                      |
| `date`                  | Дата бюллетеня                            |
| `created_on`            | Дата и время создания записи              |
| `updated_on`            | Дата и время последнего обновления записи |

## Запуск проекта

1. **Клонируйте репозиторий:**

   ```sh
   git clone <репозиторий>
   cd <папка с проектом>
   ```

2. **Установите зависимости:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**

   - Создайте `.env` файл.
   - Скопируйте в него данные из `env.example`.

4. **Запустите базу данных:**

   - Через Docker (рекомендуется):
     ```sh
     docker-compose up -d
     ```
   - Или создайте БД PostgreSQL вручную с именем `db_report` (или укажите другое имя в `.env`).

5. **Выполните миграции:**

   ```sh
   python -m db.aconfig
   ```

6. **Запустите парсер:**

   - **Асинхронный режим:**
     ```sh
     python -m parser.async_parser -y 2023
     ```
   - **Синхронный режим:**
     ```sh
     python -m parser.parser -y 2023
     ```

   *Где ****`-y`**** – это год давности файлов (по умолчанию 2023).*

## Результат

Скачанные и обработанные данные сохраняются в базу данных для дальнейшей аналитики и использования в других системах.

