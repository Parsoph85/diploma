from models import Session, Employee

session = Session()
employees = session.query(Employee).all()

if not employees:
    print("В базе данных нет сотрудников.")
else:
    print("Сотрудники в базе данных:")
    for emp in employees:
        print(f"ID: {emp.id}, Имя: {emp.name}, Должность: {emp.position}, Отдел: {emp.department.name}, Город: {emp.department.city.name}")

session.close()
