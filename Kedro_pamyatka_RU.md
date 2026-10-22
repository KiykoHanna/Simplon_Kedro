# Kedro — краткая памятка

## 1. Что такое Kedro

**Kedro** — Python-фреймворк для организации проектов обработки данных и машинного обучения.

Он помогает:
- разделять код на небольшие функции (**nodes**);
- соединять функции в последовательность (**pipeline**);
- описывать входные и выходные файлы в **Data Catalog**;
- хранить настройки отдельно от кода (**parameters**);
- повторно запускать и тестировать части проекта.

**Основная идея:** код, данные, настройки и порядок выполнения организованы отдельно.

## 2. Основные понятия

| Термин | Что означает |
|---|---|
| **Node** | Один шаг обработки: функция + входы + выходы |
| **Pipeline** | Последовательность связанных nodes |
| **Data Catalog** | Описание данных: имя, тип, путь, параметры чтения/записи |
| **Parameters** | Настройки эксперимента или обработки |
| **Pipeline registry** | Регистрация доступных pipeline |
| **Environment** | Набор конфигураций, например `base` или `dev` |

Пример цепочки:

`CSV-файлы → preprocess_companies → очищенные данные → train_model → модель`

## 3. Где что находится

Типичная структура проекта:

```text
conf/
  base/
    catalog.yml                 # пути и типы данных
    parameters.yml              # общие параметры
  dev/
    parameters_data_science.yml # настройки для dev
src/
  atelier_spaceflights/
    pipeline_registry.py        # регистрация pipeline
    pipelines/
      data_processing/
        nodes.py                # функции обработки
        pipeline.py             # сборка pipeline
      data_science/
        nodes.py                # обучение и оценка модели
        pipeline.py             # сборка pipeline
data/
  01_raw/                       # исходные данные
  02_intermediate/              # промежуточные данные
  03_primary/                   # подготовленная таблица
  06_models/                    # сохранённая модель
  07_model_output/              # предсказания
  08_reporting/                 # метрики
tests/                          # тесты
```

Номера в папках `data/` — соглашение об организации данных, а не обязательное правило Kedro.

## 4. Data Catalog: описание файлов

Файл: `conf/base/catalog.yml`

```yaml
companies:
  type: pandas.CSVDataset
  filepath: data/01_raw/companies.csv

model_input_table:
  type: pandas.ParquetDataset
  filepath: data/03_primary/model_input_table.parquet

regressor:
  type: pickle.PickleDataset
  filepath: data/06_models/regressor.pkl
```

- `companies` — имя, по которому pipeline получает данные.
- `type` — формат и способ чтения/записи.
- `filepath` — путь к файлу.

После загрузки Kedro передаёт данные в функцию, а после выполнения сохраняет выходы в указанные файлы.

## 5. Node: функция обработки

Файл: `nodes.py`

```python
def double_numbers(data):
    return data * 2
```

Функция становится node, когда её подключают в pipeline:

```python
node(
    func=double_numbers,
    inputs="numbers",
    outputs="doubled_numbers",
    name="double_numbers_node",
)
```

`inputs` и `outputs` — имена из каталога или имена промежуточных данных внутри pipeline.

## 6. Pipeline: соединение шагов

Файл: `pipeline.py`

```python
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import preprocess_companies

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=preprocess_companies,
            inputs="companies",
            outputs="preprocessed_companies",
            name="preprocess_companies_node",
        )
    ])
```

Если выход одного node совпадает со входом другого, Kedro связывает их автоматически.

В этом проекте:
- `data_processing` очищает и объединяет исходные таблицы;
- `data_science` делит данные, обучает модель и считает метрики.

## 7. Parameters: настройки отдельно от кода

Файл: `conf/base/parameters_data_science.yml`

```yaml
model_options:
  test_size: 0.2
  random_state: 3
  features:
    - engines
    - passenger_capacity
    - crew
```

В pipeline параметры передаются так:

```python
inputs=["model_input_table", "params:model_options"]
```

В функции их читают как обычный словарь:

```python
def split_data(table, options):
    features = options["features"]
```

Преимущество: можно менять настройки без изменения Python-кода.

## 8. Base и dev

- `conf/base/` — настройки по умолчанию.
- `conf/dev/` — переопределения для среды `dev`.

Пример: в `base` `test_size: 0.2`, а в `dev` `test_size: 0.3`.
Если ключ задан в `dev`, для запуска с `--env=dev` используется его значение.

## 9. Команды, которые полезно помнить

Запускать из корня проекта, где находится `pyproject.toml`.

```powershell
# Информация о проекте
uv run kedro info

# Запустить все pipeline по умолчанию
uv run kedro run

# Запустить один pipeline
uv run kedro run --pipelines=data_processing

# Запустить другой pipeline
uv run kedro run --pipelines=data_science

# Запустить с конфигурацией dev
uv run kedro run --pipelines=data_science --env=dev

# Запустить тесты
uv run pytest

# Показать доступные pipeline (если команда поддерживается версией)
uv run kedro registry list
```

Если команда `kedro registry list` не поддерживается установленной версией, посмотрите зарегистрированные pipeline в `src/atelier_spaceflights/pipeline_registry.py`.

## 10. Как добавить новый шаг

1. Написать обычную Python-функцию в `nodes.py`.
2. Подключить её через `node(...)` в `pipeline.py`.
3. Указать `inputs` и `outputs`.
4. Если вход или выход — файл, описать его в `conf/base/catalog.yml`.
5. При необходимости добавить настройки в `conf/base/parameters*.yml`.
6. Запустить нужный pipeline.
7. Добавить тест функции и проверить `uv run pytest`.

## 11. Как читать ошибку

- **Dataset not found / missing catalog entry** — проверьте имя и запись в `catalog.yml`.
- **Missing input / output** — проверьте совпадение имён в `inputs`, `outputs` и каталоге.
- **KeyError** — часто отсутствует столбец или ключ параметра; проверьте реальные названия.
- **ModuleNotFoundError** — проверьте зависимости и активное окружение; попробуйте `uv sync`.
- **Pipeline not found** — проверьте имя и регистрацию pipeline.
- **Ошибка чтения Excel** — проверьте установленный `openpyxl` и `engine` в каталоге.

## 12. Что запомнить

**Node = шаг. Pipeline = цепочка шагов. Catalog = данные и пути. Parameters = настройки.**

Типичный цикл работы:

`написать функцию → подключить node → настроить данные/параметры → запустить → проверить результат → написать тест`

## 13. Kedro-Viz: визуализация pipeline

**Kedro-Viz** — веб-интерфейс для визуального просмотра структуры pipeline: узлов, данных и связей между ними.

### Установка

В терминале PowerShell, в корне проекта:

```powershell
uv add kedro-viz
```

### Запуск

```powershell
uv run kedro viz
```

Открой адрес, указанный в терминале. Обычно это `http://127.0.0.1:4141`.

Остановить сервер: `Ctrl+C` в терминале.

### Основные элементы

- **Nodes** — функции, выполняющие отдельные шаги.
- **Datasets** — входные и выходные данные.
- **Connections / Edges** — связи между шагами.
- **Pipeline** — вся цепочка обработки данных.

В проекте `Simplon_Kedro` посмотри pipeline `data_processing` и `data_science`.

### Если не запускается

1. Убедись, что терминал открыт в папке с `pyproject.toml`.
2. Выполни `uv sync`.
3. Повтори `uv run kedro viz`.
4. При ошибке сохрани её текст для диагностики.

**Важно:** Kedro-Viz показывает структуру pipeline, а `uv run kedro run` выполняет саму обработку данных.