from flask import Flask, render_template, request, jsonify
import sqlite3 as sq

# Инициализация Flask приложения
app = Flask(__name__, template_folder='.')

# Функция для подключения к БД
def get_db_connection():
    connection = sq.connect('mvr.db')
    connection.row_factory = sq.Row
    return connection

# Инициализация базы данных
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Создание таблицы товаров если её нет
    tovari_table = ''' 
    CREATE TABLE IF NOT EXISTS tovari (
        tovar_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tovar_nm TEXT NOT NULL,
        opisanie TEXT,
        category TEXT,
        price REAL CHECK (price >= 0),
        kolvo INTEGER CHECK(kolvo >= 0),
        gorod TEXT
    )
    '''
    cursor.execute(tovari_table)
    connection.commit()
    
    # Проверка, пуста ли таблица, если да - добавляем примеры
    cursor.execute('SELECT COUNT(*) FROM tovari')
    count = cursor.fetchone()[0]
    
    if count == 0:
        example_data = [
            ('MacBook Pro', 'Мощный ноутбук для работы', 'Электроника', 99999, 5, 'Москва'),
            ('Диван', 'Удобный диван для гостиной', 'Мебель', 25000, 3, 'Москва'),
            ('Куртка', 'Зимняя куртка, размер L', 'Одежда', 3500, 10, 'Санкт-Петербург'),
        ]
        
        request_to_insert = ''' 
        INSERT INTO tovari (tovar_nm, opisanie, category, price, kolvo, gorod) 
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        for item in example_data:
            cursor.execute(request_to_insert, item)
        
        connection.commit()
    
    connection.close()

# Инициализируем БД при старте
init_db()

@app.route("/")
def index():
    """Главная страница со списком товаров"""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM tovari')
    tovari = cursor.fetchall()
    connection.close()
    
    return render_template('index.html', tovari=tovari)

@app.route("/add", methods=['GET', 'POST'])
def add_item():
    """Страница добавления нового товара"""
    if request.method == 'POST':
        tovar_nm = request.form.get('tovar_nm')
        opisanie = request.form.get('opisanie')
        category = request.form.get('category')
        price = request.form.get('price')
        kolvo = request.form.get('kolvo')
        gorod = request.form.get('gorod')
        
        if not all([tovar_nm, price, gorod]):
            return render_template('add.html', error='Заполните обязательные поля')
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            request_to_insert = ''' 
            INSERT INTO tovari (tovar_nm, opisanie, category, price, kolvo, gorod) 
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(request_to_insert, (
                tovar_nm, 
                opisanie, 
                category, 
                float(price), 
                int(kolvo) if kolvo else 0, 
                gorod
            ))
            connection.commit()
            success = True
        except Exception as e:
            success = False
        finally:
            connection.close()
        
        return render_template('add.html', success=success)
    
    return render_template('add.html')

@app.route("/api/items")
def api_items():
    """API для получения всех товаров в JSON"""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM tovari')
    tovari = cursor.fetchall()
    connection.close()
    
    return jsonify([dict(item) for item in tovari])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
