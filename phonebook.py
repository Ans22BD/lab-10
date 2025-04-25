
import psycopg2
import csv
import os

# Шаг 1: Создаём CSV-файл с контактами
csv_filename = r"C:\Users\Айдана\Desktop\Lab10-main\Lab10-main\contacts.csv"

with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['first_name', 'phone'])  # Заголовки
    writer.writerow(['Batyrkhan', '+77471530843'])
    writer.writerow(['Baga', '+77077415670'])
    writer.writerow(['Dos', '+77086809056'])

print(f"CSV-файл '{csv_filename}' создан.")

# Шаг 2: Подключение к базе данных PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",  # Убедись, что такая БД уже создана в pgAdmin
        user="postgres",
        password="Batyr2007"  # Заменить на свой пароль
    )
    print("✅ Подключение к базе данных успешно.")
except Exception as e:
    print("❌ Ошибка подключения:", e)
    exit()

cur = conn.cursor()

# Шаг 3: Создание таблицы PhoneBook
cur.execute("""
    CREATE TABLE IF NOT EXISTS PhoneBook (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE
    );
""")
conn.commit()
print("📋 Таблица PhoneBook проверена/создана.")

# Шаг 4: Загрузка данных из CSV в таблицу
with open(csv_filename, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            cur.execute("""
                INSERT INTO PhoneBook (first_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (phone) DO NOTHING;
            """, (row['first_name'], row['phone']))
        except Exception as e:
            print(f"❌ Ошибка при вставке: {e}")

conn.commit()
print("📥 Данные из CSV успешно загружены в таблицу.")

# Шаг 5: Вывод данных из таблицы
cur.execute("SELECT * FROM PhoneBook")
rows = cur.fetchall()
print("\n📞 Данные в таблице PhoneBook:")
for row in rows:
    print(row)

# Закрытие соединения
cur.close()
conn.close()
print("\n✅ Соединение с БД закрыто.")
