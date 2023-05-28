import psycopg2
from uuid import uuid4
# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password="4444")

conn.autocommit = True
cursor = conn.cursor()

# Создание таблиц судна и причалы в БД            
createtable_vessel = ("""
            CREATE TABLE IF NOT EXISTS vessels4 (
                mmsi INT PRIMARY KEY CHECK (mmsi >= 100000000 AND mmsi <= 999999999),
                name TEXT,
                year_build INTEGER,
                flag TEXT,
                vessel_type TEXT
            )
        """)
cursor.execute(createtable_vessel)

        
createtable_beth = ("""
            CREATE TABLE IF NOT EXISTS berths4 (
                berth_id INT PRIMARY KEY,
                berth_uuid TEXT,
                name TEXT,
                lat INTEGER,
                lon INTEGER,
                size INTEGER,
                moored INTEGER DEFAULT 0
            )
        """)

cursor.execute(createtable_beth)


print("Таблицы 'Причал' и 'Судна' успешно созданы!")
    
# Функция добавления судна
def add_vessel():
    mmsi = input("Введите MMSI, состоящее из 9 чисел, судна: ")
    name = input("Введите имя судна: ")
    year_build = input("Введите год строительства судна: ")
    flag = input("Введите флаг судна: ")
    vessel_type = input("Введите тип судна: ")

# Выполнение SQL-запроса для добавления судна в БД
    add_vessel = "INSERT INTO vessels4 (mmsi, name, year_build, flag, vessel_type) VALUES (%s, %s, %s, %s, %s)"
    values = (mmsi, name, year_build, flag, vessel_type)
    cursor.execute(add_vessel, values)

    print("Судно успешно добавлено!")
# Функция удаления судна
def remove_vessel():
    mmsi = input("Введите MMSI судна для удаления: ")

# Выполнение SQL-запроса для удаления судна из БД
    remove_vessel = "DELETE FROM vessels4 WHERE mmsi = %s"
    values = (mmsi,)
    cursor.execute(remove_vessel, values)

    print("Судно успешно удалено!")

# Функция обновления данных судна
def update_vessel():
    mmsi = input("Введите MMSI судна для обновления: ")
    field = input("Введите поле для обновления: ")
    value = input("Введите новое значение: ")

    if field == 'mmsi':
        print("Изменение столбца 'mmsi' недопустимо.")
        return
    
# Выполнение SQL-запроса для обновления данных судна в БД
    update_vessel = f"UPDATE vessels4 SET {field} = %s WHERE mmsi = %s "
    values = (value, mmsi)
    cursor.execute(update_vessel, values)
    print("Данные судна успешно обновлены!")



# Функция добавления причала
def add_berth():
    berth_id = input("Введите ID причала: ")
    berth_uuid = uuid4()
    name = input("Введите имя причала: ")
    lat = input("Введите широту причала: ")
    lon = input("Введите долготу причала: ")
    size = input("Введите количество судов, которое может принять причал: ")

# Выполнение SQL-запроса для добавления причала в БД
    add_berth = "INSERT INTO berths4 (berth_id, berth_uuid, name, lat, lon, size) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (berth_id, str(berth_uuid), name, lat, lon, size)
    cursor.execute(add_berth, values)

    print("Причал успешно добавлен!")

# Функция удаления причала
def remove_berth():
    berth_id = input("Введите ID причала для удаления: ")

# Выполнение SQL-запроса для удаления причала из БД
    remove_berth = "DELETE FROM berths4 WHERE berth_id = %s"
    values = (berth_id)
    cursor.execute(remove_berth, values)

    print("Причал успешно удален!")

# Функция обновления данных причала
def update_berth():
    berth_id = input("Введите ID причала для обновления: ")
    field = input("Введите поле для обновления: ")
    value = input("Введите новое значение: ")

# Выполнение SQL-запроса для обновления данных причала в БД
    update_berth = f"UPDATE berths4 SET {field} = %s WHERE berth_id = %s"
    values = (value, berth_id)
    cursor.execute(update_berth, values)

    print("Данные причала успешно обновлены!")


# Добавление столбца из одной таблицы в другую таблицу
berth_id_vessels = '''
    ALTER TABLE vessels4
    ADD COLUMN IF NOT EXISTS berth_id INTEGER REFERENCES berths4(berth_id)
'''
cursor.execute(berth_id_vessels)

# Функция пришвартовки судна
def moor_vessel():
    mmsi = input("Введите MMSI судна для пришвартовки: ")
    berth_id = input("Введите ID причала для пришвартовки судна: ")

# Проверка доступности места на причале
    moor_vessel = "SELECT size FROM berths4 WHERE berth_id = %s"
    values = (berth_id,)
    cursor.execute(moor_vessel, values)
    result = cursor.fetchone()

    if result is None:
        print("Причал с указанным ID не существует!")
        return

    berth_size = result[0]

# Подсчет количества пришвартованных судов на причале
    count_vessels = "SELECT COUNT(*) FROM vessels4 WHERE berth_id = %s"
    values = (berth_id,)
    cursor.execute(count_vessels, values)
    result = cursor.fetchone()

    if result is not None:
        current_vessels = result[0]
    else:
        current_vessels = 0

# Проверка доступности места на причале
    if current_vessels >= berth_size:
        print("На причале нет свободных мест!")
        return

# Выполнение SQL-запроса для пришвартовки судна на причал
    update_moor = "UPDATE vessels4 SET berth_id = %s WHERE mmsi = %s"
    values = (berth_id, mmsi)
    cursor.execute(update_moor, values)

    update_moored = "UPDATE berths4 SET moored = moored + 1 WHERE berth_id = %s"
    cursor.execute(update_moored, (berth_id,))
    
    print("Судно успешно пришвартовано!")

# Функция отшвартовки судна
def unmoor_vessel():
    mmsi = input("Введите MMSI судна для отшвартовки: ")

# Проверка корабля на причале
    checkship = """SELECT mmsi, berth_id FROM vessels4 WHERE mmsi = %s"""
    cursor.execute(checkship, (mmsi,))
    ship = cursor.fetchone()

    if not ship:
        print('Корабль отсутствует на причале')
        return
    
    berth_id = ship[1]
    
# Выполнение SQL-запроса для отшвартовки судна   
    unmoor = "UPDATE vessels4 SET berth_id = NULL WHERE mmsi = %s"
    cursor.execute(unmoor, (mmsi,)) 

    unmoorbeth = "UPDATE berths4 SET moored = moored - 1 WHERE berth_id = %s"
    cursor.execute(unmoorbeth, (str(berth_id)))

    print("Судно успешно отшвартовано")


# Функция просмотра всех суден
def check_vessels():
    check_vessels = """SELECT * FROM vessels4"""
    cursor.execute(check_vessels)
    print(cursor.fetchall())

# Функция просмотра всех причалов
def check_berths():
    check_berths = """SELECT * FROM berths4"""
    cursor.execute(check_berths)
    print(cursor.fetchall())

# Функция просмотра доступных причалов
def check_freeberth():
    check_freeberth = """SELECT berth_id FROM berths4 WHERE moored < size""" 
    cursor.execute(check_freeberth)
    print(cursor.fetchall())


# Цикл взаимодействия с базой данных
while True:
    command = input("Введите команду (add_vessel, remove_vessel, update_vessel, add_berth, remove_berth, update_berth, moor_vessel, unmoor_vessel, check_vessels, check_berths, check_freeberth, exit): ")

    if command == "exit":
        break

    elif command == "add_vessel":
        add_vessel()

    elif command == "remove_vessel":
        remove_vessel()

    elif command == "update_vessel":
        update_vessel()

    elif command == "add_berth" :
        add_berth()

    elif command == "remove_berth":
        remove_berth()

    elif command == "update_berth":
        update_berth()

    elif command == "moor_vessel":
        moor_vessel()

    elif command == "unmoor_vessel":
        unmoor_vessel()
    
    elif command == "check_vessels":
        check_vessels()

    elif command == "check_berths":
        check_berths()

    elif command == "check_freeberth":
        check_freeberth()
        
# Закрытие курсора и соединения с базой данных
cursor.close()
conn.close()

