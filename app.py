# Импорт необходимых модулей из Flask для создания веб-приложения
from flask import Flask, render_template, request, jsonify, redirect, url_for
# Импорт классов моделей и сессии из модуля models для работы с базой данных
from models import Session, City, Department, Employee
# Импорт функции инициализации базы данных
from models import init_db
# Импорт joinedload для оптимизации запросов (избегание DetachedInstanceError)
from sqlalchemy.orm import joinedload
# Импорт func и or_ из SQLAlchemy для case-insensitive поиска и объединения условий
from sqlalchemy import func, or_

# Создание экземпляра Flask-приложения
app = Flask(__name__)
# Инициализация базы данных (создание таблиц, если они не существуют)
init_db()

# Маршрут для главной страницы (GET-запрос по умолчанию)
@app.route('/')
def index():
    # Рендерит шаблон index.html (главная страница приложения)
    return render_template('index.html')

# Маршрут для страницы поиска (GET-запрос)
@app.route('/search')
def search():
    # Рендерит шаблон search.html (форма для ввода поискового запроса)
    return render_template('search.html')

# Маршрут для обработки результатов поиска (POST-запрос, принимает JSON)
@app.route('/search_results', methods=['POST'])
def search_results():
    # Получаем поисковый запрос из JSON-тела запроса, удаляем пробелы по краям
    # Flask автоматически обрабатывает UTF-8, так что русские символы корректны
    query = request.json.get('query', '').strip()

    # Если запрос пустой, возвращаем пустой массив результатов
    if not query:
        return jsonify([])

    # Создаем новую сессию для работы с базой данных
    session = Session()
    try:
        # Выполняем запрос к таблице Employee с предварительной загрузкой связанных данных
        # (department и city) для избежания DetachedInstanceError
        # Фильтр: case-insensitive поиск с использованием func.lower() для корректной
        # обработки кириллицы (в отличие от Python's lower(), который не работает с русским регистром)
        # Используем or_ для объединения условий поиска по нескольким полям
        results = session.query(Employee).options(joinedload(Employee.department).joinedload(Department.city)) \
            .filter(
                or_(
                    func.lower(Employee.name).like(func.lower(f'%{query}%')),          # Поиск по имени
                    func.lower(Employee.position).like(func.lower(f'%{query}%')),      # Поиск по должности
                    func.lower(Department.name).like(func.lower(f'%{query}%')),        # Поиск по названию отдела
                    func.lower(City.name).like(func.lower(f'%{query}%'))               # Поиск по названию города
                )
            ).all()

        # Формируем список словарей с результатами для отправки в JSON
        employees = []
        for emp in results:
            employees.append({
                'id': emp.id,
                'name': emp.name,
                'position': emp.position,
                'department': emp.department.name if emp.department else 'Нет',  # Название отдела или "Нет"
                'city': emp.department.city.name if emp.department and emp.department.city else 'Нет'  # Название города или "Нет"
            })

        # Возвращаем результаты в формате JSON
        return jsonify(employees)

    # Обработка исключений (например, ошибки базы данных)
    except Exception as e:
        print(f"ERROR: Ошибка в поиске: {str(e)}")  # Логируем ошибку в консоль
        return jsonify({'error': 'Ошибка поиска'}), 500  # Возвращаем ошибку с кодом 500
    finally:
        # Закрываем сессию в любом случае для освобождения ресурсов
        session.close()

# Маршрут для страницы добавления сотрудника (GET-запрос)
@app.route('/add')
def add():
    # Создаем сессию для запроса к базе данных
    session = Session()
    # Загружаем все отделы с предварительной загрузкой связанных городов
    # (для отображения в форме: "Название отдела (Город)")
    departments = session.query(Department).options(joinedload(Department.city)).all()
    # Закрываем сессию
    session.close()
    # Рендерим шаблон add.html, передавая список отделов для выпадающего списка
    return render_template('add.html', departments=departments)

# Маршрут для обработки формы добавления сотрудника (POST-запрос)
@app.route('/add_employee', methods=['POST'])
def add_employee():
    # Создаем сессию для работы с базой данных
    session = Session()
    try:
        # Извлекаем данные из формы (уже в UTF-8 благодаря Flask)
        name = request.form['name']              # Имя сотрудника
        position = request.form['position']      # Должность
        department_id = int(request.form['department_id'])  # ID отдела (преобразуем в int)

        # Создаем новый объект Employee
        emp = Employee(name=name, position=position, department_id=department_id)
        # Добавляем в сессию и коммитим изменения (сохраняем в БД)
        session.add(emp)
        session.commit()
    # Обработка исключений (например, ошибки валидации или БД)
    except Exception as e:
        session.rollback()  # Откатываем изменения при ошибке
    finally:
        # Закрываем сессию
        session.close()

    # Перенаправляем на главную страницу после добавления
    return redirect(url_for('index'))

# Запуск приложения в режиме отладки (только если файл запущен напрямую)
if __name__ == '__main__':
    app.run(debug=True)
