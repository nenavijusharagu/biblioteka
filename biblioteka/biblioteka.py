# Импорт необходимых библиотек
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Функция для создания таблиц в базе данных
def create_tables():
    # Подключение к базе данных
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()

    # Создание таблицы книг
    cur.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    year INTEGER,
                    publisher TEXT,
                    code TEXT UNIQUE,
                    issued INTEGER DEFAULT 0
                )''')

    # Создание таблицы читателей
    cur.execute('''CREATE TABLE IF NOT EXISTS borrowers (
                    id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    phone_number TEXT,
                    card_number TEXT UNIQUE
                )''')

    # Создание таблицы выданных книг
    cur.execute('''CREATE TABLE IF NOT EXISTS issued_books (
                    id INTEGER PRIMARY KEY,
                    book_id INTEGER,
                    borrower_id INTEGER,
                    issue_date DATE,
                    return_date DATE,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
                )''')


    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()

# Функция для обновления информации о книгах
def update_books_info():
    # Очистка таблицы книг перед обновлением
    for i in book_tree.get_children():
        book_tree.delete(i)

    # Подключение к базе данных
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    # Получение информации о книгах из базы данных
    cur.execute('''SELECT books.id, books.title, books.author, books.year, books.publisher, books.code, 
                          borrowers.full_name, issued_books.issue_date, issued_books.return_date 
                   FROM books 
                   LEFT JOIN issued_books ON books.id = issued_books.book_id 
                   LEFT JOIN borrowers ON issued_books.borrower_id = borrowers.id''')
    books_info = cur.fetchall()
    # Закрытие соединения с базой данных
    conn.close()

    # Вставка информации о книгах в таблицу
    for book_info in books_info:
        book_tree.insert('', 'end', values=book_info)
# Функция для обновления информации о читателях        
def update_borrowers_info():
    # Очистка таблицы читателей перед обновлением
    for i in borrower_tree.get_children():
        borrower_tree.delete(i)
    # Подключение к базе данных
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    # Получение информации о читателях из базы данных
    cur.execute("SELECT full_name, phone_number, card_number FROM borrowers")
    borrowers_info = cur.fetchall()
    conn.close()

    # Вставка информации о читателях в таблицу
    for borrower_info in borrowers_info:
        borrower_tree.insert('', 'end', values=(borrower_info[0], borrower_info[1], borrower_info[2]))

# Функция для добавления книги в базу данных
def add_book(title, author, year, publisher, code):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    try:
        # Вставка данных о книге в таблицу
        cur.execute("INSERT INTO books (title, author, year, publisher, code) VALUES (?, ?, ?, ?, ?)", (title, author, year, publisher, code))
        conn.commit()
    except sqlite3.IntegrityError:
        # Вывод сообщения об ошибке, если книга с таким шифром уже существует
        messagebox.showerror("Ошибка", "Книга с таким шифром уже существует!")
    finally:
        conn.close()
        update_books_info()

# Добавление читателя в базу данных
def add_borrower(full_name, phone_number, card_number):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO borrowers (full_name, phone_number, card_number) VALUES (?, ?, ?)", (full_name, phone_number, card_number))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Читатель с таким номером читательского билета уже существует!")
    finally:
        conn.close()
        update_borrowers_info()

# Выдача книги читателю
def issue_book(book_id, borrower_id, issue_date):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO issued_books (book_id, borrower_id, issue_date) VALUES (?, ?, ?)", (book_id, borrower_id, issue_date))
    cur.execute("UPDATE books SET issued = 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    update_books_info()

# Возврат книги читателю
def return_book(issued_book_id, return_date):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("UPDATE issued_books SET return_date = ? WHERE id = ?", (return_date, issued_book_id))
    issued_book = cur.execute("SELECT books.title, borrowers.full_name, borrowers.phone_number, issued_books.issue_date FROM issued_books JOIN books ON issued_books.book_id = books.id JOIN borrowers ON issued_books.borrower_id = borrowers.id WHERE issued_books.id = ?", (issued_book_id,)).fetchone()
    conn.commit()
    conn.close()
    update_books_info()
    return issued_book

# Удаление книги из базы данных
def delete_book(book_id):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при удалении книги: {e}")
    finally:
        conn.close()
        update_books_info()

# Удаление читателя из базы данных
def delete_borrower(borrower_id): 
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM borrowers WHERE id = ?', (borrower_id,))
        conn.commit()
        update_borrowers_info()  # Обновляем таблицу после удаления читателя
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при удалении читателя: {e}")
    finally:
        conn.close()

# Функция для обновления списка доступных книг при выборе книги для выдачи        
def update_book_options(book_var, book_menu):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    # Получение списка доступных книг (не выданных)
    cur.execute("SELECT id, title FROM books WHERE issued = 0")
    books = cur.fetchall()
    conn.close()

    book_options = [book[1] for book in books]
    book_var.set("")
    book_menu['menu'].delete(0, 'end')

    # Добавление опций выбора книги в выпадающее меню
    for book in book_options:
        book_menu['menu'].add_command(label=book, command=tk._setit(book_var, book))

# Функция для обновления списка доступных читателей при выборе читателя для выдачи книги
def update_borrower_options(borrower_var, borrower_menu):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    # Получение списка читателей
    cur.execute("SELECT id, full_name FROM borrowers")
    borrowers = cur.fetchall()
    conn.close()

    borrower_options = [borrower[1] for borrower in borrowers]
    borrower_var.set("")
    borrower_menu['menu'].delete(0, 'end')

    # Добавление опций выбора читателя в выпадающее меню
    for borrower in borrower_options:
        borrower_menu['menu'].add_command(label=borrower, command=tk._setit(borrower_var, borrower))

# Функция для обновления информации о читателях 
def update_borrowers_info():
    for i in borrower_tree.get_children():
        borrower_tree.delete(i)

    # Подключение к базе данных SQLite и выполнение запроса на получение информации о читателях
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, phone_number, card_number FROM borrowers")
    borrowers_info = cur.fetchall()
    conn.close()

    # Вставка информации о читателях в таблицу
    for borrower_info in borrowers_info:
        borrower_tree.insert('', 'end', values=borrower_info)

# Функция для открытия окна добавления книги
def add_book_window():
    # Создание нового окна
    add_book_window = tk.Toplevel(main_window)
    add_book_window.title("Добавить книгу")

    # Создание меток и полей для ввода информации о книге
    title_label = tk.Label(add_book_window, text="Название книги:")
    title_label.pack(pady=5)
    title_entry = tk.Entry(add_book_window)
    title_entry.pack(pady= 5)

    author_label = tk.Label(add_book_window, text="Автор:")
    author_label.pack(pady=5)
    author_entry = tk.Entry(add_book_window)
    author_entry.pack(pady=5)

    year_label = tk.Label(add_book_window, text="Год издания:")
    year_label.pack(pady=5)
    year_entry = tk.Entry(add_book_window)
    year_entry.pack(pady=5)

    publisher_label = tk.Label(add_book_window, text="Издательство:")
    publisher_label.pack(pady=5)
    publisher_entry = tk.Entry(add_book_window)
    publisher_entry.pack(pady=5)

    code_label = tk.Label(add_book_window, text="Шифр книги:")
    code_label.pack(pady=5)
    code_entry = tk.Entry(add_book_window)
    code_entry.pack(pady=5)

    # Функция для добавления книги в базу данных
    def add_book_to_db():
        # Получение информации о книге из полей ввода
        title = title_entry.get()
        author = author_entry.get()
        year = year_entry.get()
        publisher = publisher_entry.get()
        code = code_entry.get()
        # Вызов функции добавления книги в базу данных и обновление информации
        add_book(title, author, year, publisher, code)
        add_book_window.destroy()
        update_books_info()
    # Кнопка для добавления книги
    add_button = tk.Button(add_book_window, text="Добавить", command=add_book_to_db)
    add_button.pack(pady=5)

# Функция для открытия окна добавления читателя
def add_borrower_window():
    add_borrower_window = tk.Toplevel(main_window)
    add_borrower_window.title("Добавить читателя")

    full_name_label = tk.Label(add_borrower_window, text="ФИО:")
    full_name_label.pack(pady=5)
    full_name_entry = tk.Entry(add_borrower_window)
    full_name_entry.pack(pady=5)

    phone_label = tk.Label(add_borrower_window, text="Номер телефона:")
    phone_label.pack(pady=5)
    phone_entry = tk.Entry(add_borrower_window)
    phone_entry.pack(pady=5)

    card_label = tk.Label(add_borrower_window, text="Номер читательского билета:")
    card_label.pack(pady=5)
    card_entry = tk.Entry(add_borrower_window)
    card_entry.pack(pady=5)

    # Функция для добавления читателя в базу данных
    def add_borrower_to_db():
        full_name = full_name_entry.get()
        phone_number = phone_entry.get()
        card_number = card_entry.get()
        add_borrower(full_name, phone_number, card_number)
        add_borrower_window.destroy()
        update_borrowers_info()

    add_button = tk.Button(add_borrower_window, text="Добавить", command=add_borrower_to_db)
    add_button.pack(pady=5)

# Функция для открытия окна выдачи книги
def issue_book_window():
    issue_book_window = tk.Toplevel(main_window)
    issue_book_window.title("Выдать книгу")

    book_label = tk.Label(issue_book_window, text="Книга:")
    book_label.pack(pady=5)
    book_var = tk.StringVar(issue_book_window)
    book_menu = tk.OptionMenu(issue_book_window, book_var, "")
    book_menu.pack(pady=5)

    # Обновление списка доступных книг для выбора
    update_book_options(book_var, book_menu)

    borrower_label = tk.Label(issue_book_window, text="Читатель:")
    borrower_label.pack(pady=5)
    borrower_var = tk.StringVar(issue_book_window)
    borrower_menu = tk.OptionMenu(issue_book_window, borrower_var, "")
    borrower_menu.pack(pady=5)

    # Обновление списка читателей для выбора
    update_borrower_options(borrower_var, borrower_menu)

    date_label = tk.Label(issue_book_window, text="Дата выдачи:")
    date_label.pack(pady=5)
    date_entry = tk.Entry(issue_book_window)
    date_entry.pack(pady=5)

#Обработка выдачи выбранной книги читателю
    def issue_book_to_borrower():
        book = book_var.get()
        borrower = borrower_var.get()
        issue_date = date_entry.get()
        # Получение ID книги и читателя из базы данных
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM books WHERE title = ?", (book,))
        book_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM borrowers WHERE full_name = ?", (borrower,))
        borrower_id = cur.fetchone()[0]
        conn.close()

        # Выдача книги читателю и обновление информации
        issue_book(book_id, borrower_id, issue_date)
        issue_book_window.destroy()
        update_books_info()

    issue_button = tk.Button(issue_book_window, text="Выдать", command=issue_book_to_borrower)
    issue_button.pack(pady=5)

# Функция для открытия окна возврата книги
def return_book_window():
    return_book_window = tk.Toplevel(main_window)
    return_book_window.title("Вернуть книгу")

    issued_books_label = tk.Label(return_book_window, text="Выданные книги:")
    issued_books_label.pack(pady=5)
    issued_books_var = tk.StringVar(return_book_window)
    issued_books_menu = tk.OptionMenu(return_book_window, issued_books_var, "")
    issued_books_menu.pack(pady=5)

    # Получение списка выданных книг из базы данных
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT issued_books.id, books.title, borrowers.full_name FROM issued_books JOIN books ON issued_books.book_id = books.id JOIN borrowers ON issued_books.borrower_id = borrowers.id WHERE issued_books.return_date IS NULL")
    issued_books = cur.fetchall()
    conn.close()

    # Формирование списка книг для выбора в окне возврата
    issued_books_options = [f"{issued_book[1]} - {issued_book[2]}" for issued_book in issued_books]
    issued_books_var.set("")
    issued_books_menu['menu'].delete(0, 'end')

    for issued_book in issued_books_options:
        issued_books_menu['menu'].add_command(label=issued_book, command=tk._setit(issued_books_var, issued_book))

    return_date_label = tk.Label(return_book_window, text="Дата возврата:")
    return_date_label.pack(pady=5)
    return_date_entry = tk.Entry(return_book_window)
    return_date_entry.pack(pady=5)

#Обработка возврата выбранной книги читателем
    def return_issued_book():
        issued_book = issued_books_var.get()
        return_date = return_date_entry.get()
        issued_book_id = issued_books[issued_books_options.index(issued_book)][0]

        returned_book = return_book(issued_book_id, return_date)
        messagebox.showinfo("Возвращена книга", f"Книга '{returned_book[0]}' возвращена читателем {returned_book[1]}, телефон {returned_book[2]}, дата выдачи: {returned_book[3]}")
        return_book_window.destroy()
        update_books_info()

    return_button = tk.Button(return_book_window, text="Вернуть", command=return_issued_book)
    return_button.pack(pady=5)

# Создание таблицы для отображения книг
def book_tree():
    book_frame = ttk.Frame(main_window)
    book_frame.pack(pady=10)
    book_tree = ttk.Treeview(book_frame, columns=("id", "title", "author", "year", "publisher", "code", "borrower", "issue_date", "return_date"), show="headings")
    book_tree.heading("id", text="ID")
    book_tree.heading("title", text="Название")
    book_tree.heading("author", text="Автор")
    book_tree.heading("year", text="Год")
    book_tree.heading("publisher", text="Издательство")
    book_tree.heading("code", text="Шифр")
    book_tree.heading("borrower", text="Читатель")
    book_tree.heading("issue_date", text="Дата выдачи")
    book_tree.heading("return_date", text="Дата возврата")
    book_tree.column("id", width=50)
    book_tree.column("title", width=150)
    book_tree.column("author", width=100)
    book_tree.column("year", width=50)
    book_tree.column("publisher", width=100)
    book_tree.column("code", width=50)
    book_tree.column("borrower", width=100)
    book_tree.column("issue_date", width=100)
    book_tree.column("return_date", width=100)
    book_tree.pack()

    return book_tree

# Создание таблицы для отображения читателей
def borrower_tree():
    borrower_frame = ttk.Frame(main_window)
    borrower_frame.pack(pady=10)
    borrower_tree = ttk.Treeview(borrower_frame, columns=("id", "full_name", "phone_number", "card_number"), show="headings")
    borrower_tree.heading("id", text="ID")
    borrower_tree.heading("full_name", text="ФИО")
    borrower_tree.heading("phone_number", text="Номер телефона")
    borrower_tree.heading("card_number", text="Номер билета")
    borrower_tree.column("id", width=50)
    borrower_tree.column("full_name", width=150)
    borrower_tree.column("phone_number", width=100)
    borrower_tree.column("card_number", width=100)
    borrower_tree.pack()
    
    return borrower_tree

# Основная часть программы
if __name__ == "__main__":
    # Создание таблиц в базе данных
    create_tables()
    # Создание главного окна приложения
    main_window = tk.Tk()
    main_window.title("Библиотека")
    # Создание таблицы для отображения информации о книгах
    book_tree = book_tree()
    # Создание таблицы для отображения информации о читателях
    borrower_tree = borrower_tree()

    # Панель кнопок
    button_frame = ttk.Frame(main_window)
    button_frame.pack(pady=10)
    
    # Создание кнопок для различных действий
    add_book_button = tk.Button(button_frame, text="Добавить книгу", command=add_book_window)
    add_book_button.grid(row=0, column=0, padx=5)
    
    add_borrower_button = tk.Button(button_frame, text="Добавить читателя", command=add_borrower_window)
    add_borrower_button.grid(row=0, column=1, padx=5)
    
    issue_book_button = tk.Button(button_frame, text="Выдать книгу", command=issue_book_window)
    issue_book_button.grid(row=0, column=2, padx=5)
    
    return_book_button = tk.Button(button_frame, text="Вернуть книгу", command=return_book_window)
    return_book_button.grid(row=0, column=3, padx=5)

    delete_book_button = tk.Button(button_frame, text="Удалить книгу", command=lambda: delete_book(book_tree.item(book_tree.selection()[0])['values'][0]))
    delete_book_button.grid(row=0, column=4, padx=5)

    delete_borrower_button = tk.Button(button_frame, text="Удалить читателя", command=lambda: delete_borrower(borrower_tree.item(borrower_tree.selection()[0])['values'][0]))
    delete_borrower_button.grid(row=0, column=5, padx=5)

#Отображение данных
    def display_data():
        update_books_info()
        update_borrowers_info()

    display_data_button = tk.Button(button_frame, text="Отобразить данные", command=display_data)
    display_data_button.grid(row=0, column=6, padx=5)
    
    # Запуск основного цикла программы
    main_window.mainloop()
