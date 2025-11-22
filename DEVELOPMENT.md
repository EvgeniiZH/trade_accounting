# Trade Accounting - Локальное окружение разработки

## Как мы работаем над проектом

1. **Основная ветка разработки — `develop`.** Перед задачей: `git pull origin develop`, затем ветка в формате `feature/<issue>` или `bugfix/<issue>`.
2. **Фиксация знаний — в репозитории.** Все настройки среды, команды и решения проблем записываем сюда (в этот файл и `README.md`). Никаких “устных” хаков.
3. **Каждая задача = отдельный PR.** Перед пушем запускаем миграции/тесты локально.
4. **Деплой:** staging обновляется автоматически из `develop`, production — вручную из `main`.

## Быстрый старт без Docker (Windows/macOS/Linux)

```bash
git clone git@github.com:EvgeniiZH/trade_accounting.git
cd trade_accounting
python -m venv venv
source venv/bin/activate        # или .\venv\Scripts\activate в Windows
pip install --upgrade pip
pip install -r requirements.txt
cp env.example .env             # укажи SECRET_KEY и ALLOWED_HOSTS
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Сервер слушает `http://127.0.0.1:8000`.
- БД по умолчанию — SQLite (`db.sqlite3` в корне). Для Postgres задай `DATABASE_URL` или `POSTGRES_*` в `.env`.
- Чтобы отключить кэш шаблонов: убедись, что `DJANGO_ENV=local`.

## Локальная разработка через Docker

### Запуск
```bash
docker compose -f docker-compose.local.yml up -d --build
```

### Остановка
```bash
docker compose -f docker-compose.local.yml down
```

### Полезные команды:

**Применить миграции:**
```bash
docker compose -f docker-compose.local.yml exec web python manage.py migrate
```

**Создать суперпользователя:**
```bash
docker compose -f docker-compose.local.yml exec web python manage.py createsuperuser
```

**Просмотр логов:**
```bash
docker compose -f docker-compose.local.yml logs -f web
docker compose -f docker-compose.local.yml logs -f db
```

**Доступ к базе данных:**
```bash
docker compose -f docker-compose.local.yml exec db psql -U django -d django_project_db
```

**Выполнить команды Django:**
```bash
docker compose -f docker-compose.local.yml exec web python manage.py <command>
```

## Ежедневный рабочий цикл

1. `git checkout develop && git pull`.
2. `git checkout -b feature/<имя-задачи>`.
3. Запуск окружения (venv или Docker) + `python manage.py runserver`.
4. После изменений:
   - `python manage.py makemigrations` (если нужны миграции) и `python manage.py migrate`.
   - `python manage.py test`.
5. `git commit -am "описание"` → `git push origin feature/...`.
6. Создать Pull Request в `develop`. Автотесты пройдут в GitHub Actions.

## Автодеплой (GitHub Actions)

### Staging (ветка `develop`):
- Файл: `.github/workflows/staging.yml`
- Срабатывает при push в ветку `develop`
- Требуемые секреты GitHub:
  - `STAGING_SSH_PRIVATE_KEY` - SSH ключ для доступа к серверу
  - `STAGING_SERVER_IP` - IP адрес сервера staging
  - `STAGING_SSH_USER` - пользователь SSH (по умолчанию `root`)

### Production (ручной запуск workflow `Release`)
- Берёт код из `main`.
- Требуемые секреты GitHub:
  - `PROD_SSH_PRIVATE_KEY`
  - `PROD_SERVER_IP`
  - `PROD_SSH_USER`
  - `GHCR_PAT`

## Файлы окружения

### Локально
- `.env` — копия `env.example`. Обязательные поля: `DJANGO_ENV`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL` (или `POSTGRES_*`).

### Staging
- `.env.staging` на сервере `/opt/trade_accounting_staging/.env`.

### Production
- `.env.production` на сервере `/opt/trade_accounting/.env`.

## Структура Docker Compose файлов

- `docker-compose.yml` - базовый файл для production
- `docker-compose.local.yml` - для локальной разработки
- `docker-compose.staging.yml` - для staging окружения

## Проверка работоспособности

1. **Проверка веб-сервера:**
   ```bash
   curl http://127.0.0.1:8000
   ```

2. **Проверка базы данных:**
   ```bash
   docker-compose -f docker-compose.local.yml exec web python manage.py check --database default
   ```

3. **Проверка миграций:**
   ```bash
   docker-compose -f docker-compose.local.yml exec web python manage.py showmigrations
   ```

## Проверочный чек-лист перед PR

- [ ] Обновил ветку из `develop`.
- [ ] Добавил/обновил `.env.example`, если нужны новые переменные.
- [ ] Прогнал `python manage.py test`.
- [ ] Добавил миграции (если менялись модели).
- [ ] Обновил документацию/комментарии (как минимум этот файл или README, если затронуты процессы).

## UI / CSS правила (обновлено)

Чтобы обеспечить стабильный пользовательский интерфейс и избежать обрезания фокусов/бордеров при вводе, придерживайтесь следующих правил:

- **Глобальный скролл страницы должен быть отключён.** Страница не должна прокручиваться целиком — прокрутка должна происходить внутри рабочих блоков. Для этого используйте:
  - `.content-area { overflow: hidden; }`
  - `.page-wrapper { overflow-y: hidden; }`
  - `.page-content { overflow-y: auto; }` — основной контейнер контента отвечает за вертикальную прокрутку карточки/страницы.

- **Таблицы с большим количеством строк — внутренний скролл.** Оборачивайте таблицы в контейнер с классом `.table-scroll` и давайте ему `overflow-y: auto; max-height: 70vh;`.

- **Фиксированные заголовки таблиц.** Заголовки таблиц делайте `position: sticky; top: 0; z-index: 6;` на `thead`.

- **Избегайте `overflow: hidden` на родительских контейнерах форм и колонок.** Это режет внешнюю обводку фокуса поля ввода. Если нужно ограничить ширину — используйте `padding` и `box-sizing`, но оставляйте `overflow` видимым у контейнеров, содержащих интерактивные элементы.

- **Sticky/плавающие элементы и z-index.** При использовании `position: sticky` корректно выставляйте `z-index` чтобы заголовки были сверху над содержимым.

- **Проверка в браузере (быстрая диагностика):**
  1. Откройте страницу и выполните в консоли браузера:
     ```js
     getComputedStyle(document.body).overflow
     getComputedStyle(document.documentElement).overflow
     getComputedStyle(document.querySelector('.page-content')).overflowY
     ```
  2. Убедитесь, что `body`/`html` — `hidden`, а `.page-content` — `auto`.

Эти правила записаны после практической правки: при работе над страницей "Создание расчёта" мы отключили глобальную прокрутку и оставили прокрутку внутри `.page-content` и `.table-scroll`, чтобы фокусные бордеры не обрезались.

