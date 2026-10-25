# Test-Me: автотести UI та API

Автотести для навчального магазину [Test-Me](https://test-me.vzl.one/): **99 тестів** (88 API + 11 UI, зокрема мобільний екран 360px) на Python, pytest, Selenium і requests. Звіт — Allure.

**📊 Звіт останнього запуску:** https://musthav6.github.io/test-me-qa/

## Чому в звіті є червоні тести

Сайт навмисно містить дефекти, а тести перевіряють поведінку з технічного завдання, а не підлаштовуються під помилки. Тому **89 тестів проходять, 10 падають — і так має бути**: кожне падіння — це знайдена розбіжність із ТЗ. З тієї ж причини запуск у GitHub позначається червоним хрестиком.

| Тест, що падає | Що не так на сайті |
|---|---|
| `test_coupon_gives_10_percent_on_goods[welcome10]`, `[Welcome10]` | Промокод у нижньому регістрі не приймається (BUG-002) |
| `test_standard_shipping_threshold[exactly threshold]` | На рівно 1 500 грн доставка не безкоштовна (BUG-003) |
| `test_search_by_part_of_name[lower case]`, `[upper case]` | Пошук чутливий до регістру (BUG-008) |
| `test_invalid_contacts_return_422[name 1 char after trim]` | Ім'я з 1 символу після trim приймається (BUG-009) |
| `test_repeated_cancel_returns_409` | Повторне скасування дає 200 замість 409 (BUG-010) |
| `test_text_length_after_trim[500 chars after trim]` | Відгук 500 символів із пробілами по краях відхиляється |
| `test_adding_same_product_increases_quantity[lowest stock product]` | «Фокус» додається в кошик окремими рядками (BUG-004) |
| `test_cart_and_coupon_survive_reload` | Промокод зникає після перезавантаження сторінки (BUG-005) |

Опис кожного дефекту зі скріншотами — у [docs/bugs.md](docs/bugs.md).

## Запустити в GitHub (нічого не встановлюючи)

1. Відкрити вкладку **[Actions](https://github.com/musthav6/test-me-qa/actions)** → зліва **Tests**.
2. Справа натиснути **Run workflow** → вибрати, що запускати (`all` — усе, `api` або `ui`) → зелена кнопка **Run workflow**.
3. Зачекати ~3 хвилини, поки запуск завершиться.
4. Відкрити звіт: https://musthav6.github.io/test-me-qa/ (оновлюється після кожного запуску).

Кнопка **Run workflow** доступна власнику репозиторію та співавторам. Щоб запустити у себе: **Fork** (угорі справа) → у своїй копії **Settings → Pages → Source: GitHub Actions** → далі кроки 1–3; звіт з'явиться на `https://<ваш-логін>.github.io/test-me-qa/`.

## Запустити на своєму комп'ютері

**1. Встановити програми** (один раз):

- [Python 3.12 або новіший](https://www.python.org/downloads/) — на Windows у першому вікні встановлювача поставити галочку **Add python.exe to PATH**;
- [Google Chrome](https://www.google.com/chrome/);
- [Node.js LTS](https://nodejs.org/) — потрібен лише для звіту Allure.

На Windows усе разом можна поставити однією командою в PowerShell:

```powershell
winget install Python.Python.3.12 Google.Chrome OpenJS.NodeJS.LTS
```

**2. Завантажити проєкт:** на сторінці репозиторію **Code → Download ZIP** і розпакувати, або `git clone https://github.com/musthav6/test-me-qa.git`.

**3. Запустити:** відкрити термінал у папці проєкту (у Windows: у папці правою кнопкою → **Open in Terminal**) і ввести:

```bash
python run_tests.py
```

Скрипт сам створить віртуальне оточення `.venv`, встановить залежності, запустить усі тести в 4 потоки (~2–3 хвилини) і відкриє звіт у браузері. Щоб закрити звіт, натиснути `Ctrl+C` у терміналі.

Інші варіанти:

```bash
python run_tests.py -m api                                  # лише API
python run_tests.py -m ui                                   # лише UI
python run_tests.py tests/ui/test_checkout.py --headed      # один файл, браузер видно на екрані
```

На macOS і Linux замість `python` може знадобитися `python3`.

### Де шукати результати

| Що | Де |
|---|---|
| Підсумок | У терміналі наприкінці: `10 failed, 89 passed` |
| Звіт | Відкривається в браузері сам (адреса `http://localhost:…`). Відкрити ще раз: `npx allure@3.22.1 open allure-results` |
| Сирі результати | Папка `allure-results/` (перезаписується при кожному запуску) |
| Скріншоти падінь UI | У звіті: тест → вкладка з вкладеннями `screenshot` і `url`. На диску — файли `allure-results/*-attachment.png` |
| Звіт як файли | `npx allure@3.22.1 generate allure-results -o allure-report` → папка `allure-report/` |

## Що покрито

- **API:** каталог і фільтри, обране, відгуки, розрахунок кошика (промокод, доставка, межі), оформлення й валідація, замовлення та скасування, авторизація та ізоляція середовищ.
- **UI:** наскрізна покупка за зразком із ТЗ, подвійний клік на «Оформити», кошик і промокод після reload, повторне додавання товару, HTML у відгуку не виконується, фільтр і пошук замовлень, покупка на екрані 360px.
- **Паралельність:** `-n 4`, кожен тест створює власне середовище (token).
- **Стабільність:** 10 повних прогонів поспіль (`-n 4`, по 2–3 хв): щоразу 89 passed і ті самі 10 failed, 0 errors — жодного нестабільного тесту.

Поза покриттям (з причинами): доступність і мережеві помилки (наступний крок), порівняння товарів і «Почати заново» (перевірено вручну), строк token 24 год, округлення знижки. Детально — у [тест-плані](docs/test-plan.md).

## Документація

- [docs/test-plan.md](docs/test-plan.md) — тест-план: стратегія, пріоритети, ризики, поза покриттям.
- [docs/test-cases.md](docs/test-cases.md) — тест-кейси у форматі зразка з ТЗ, зі зв'язком на автотести.
- [docs/bugs.md](docs/bugs.md) — баг-репорти зі скріншотами.

## Структура проєкту

```text
api/            клієнт API (token, повтор на 429) і функції ендпоінтів
helpers/        catalog.py — підбір товарів за властивістю; pricing.py — очікувані суми за ТЗ
pages/          Page Objects для UI: магазин, кошик, замовлення, картка товару
tests/api/      API-тести
tests/ui/       UI-тести (Selenium)
conftest.py     фікстури: середовища, браузер, скріншот при падінні UI
run_tests.py    запуск однією командою
.github/        GitHub Actions: запуск кнопкою і публікація звіту
docs/           тест-план, тест-кейси, баг-репорти, скріншоти
```

## Для розробників

Без скрипта, у власному віртуальному оточенні:

```bash
pip install -r requirements.txt
pytest -n 4            # усе паралельно
pytest -m ui --headed  # UI з вікном браузера
pytest -k "coupon"     # тести за частиною назви
```

