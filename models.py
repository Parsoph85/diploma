from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///employees.db', echo=True)
Session = sessionmaker(bind=engine)


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    departments = relationship("Department", back_populates="city")


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship("City", back_populates="departments")
    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False, default='Специалист')
    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship("Department", back_populates="employees")


# Создание таблиц и пример данных
def init_db():
    Base.metadata.create_all(engine)
    session = Session()
    # Проверяем, есть ли данные
    if session.query(City).count() == 0:
        # Города
        city1 = City(name='Москва')
        city2 = City(name='Санкт-Петербург')
        session.add_all([city1, city2])
        session.commit()

        # Отделы
        dept1 = Department(name='IT', city=city1)
        dept2 = Department(name='HR', city=city1)
        dept3 = Department(name='Sales', city=city2)
        session.add_all([dept1, dept2, dept3])
        session.commit()

        # Сотрудники
        emp1 = Employee(name='Иван Иванов', position='Разработчик', department=dept1)
        emp2 = Employee(name='Мария Петрова', position='Менеджер', department=dept2)
        emp3 = Employee(name='Петр Сидоров', position='Аналитик', department=dept1)
        emp4 = Employee(name='Анна Козлова', position='Специалист', department=dept3)
        emp5 = Employee(name='Дмитрий Волков', position='Директор', department=dept3)
        session.add_all([emp1, emp2, emp3, emp4, emp5])
        session.commit()
    session.close()


if __name__ == '__main__':
    init_db()
