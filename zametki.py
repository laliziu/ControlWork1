from tkinter import *
from tkinter.messagebox import showerror, askyesno, showinfo
import sqlite3
from pathlib import Path

file = Path('zametki.py')
file.touch(exist_ok=True)

db = sqlite3.connect("notes.db")
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS notes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT,
    content TEXT
);""")
db.commit()

root = Tk()
root.title("Заметки")
root.geometry("300x500")

def note(*args, update_func=None):
    if args:
        cur.execute("SELECT id, name, content FROM notes WHERE id = ?", args)
        id, name, content = cur.fetchone()

    window = Toplevel()
    if args:
        window.title(name)
    else:
        window.title("Новая заметка")
    window.geometry("400x500")

    def save(*_):
        nonlocal entry, text, update_func, window, args

        if not entry.get():
            showerror("Ошибка", "Укажите название заметки")
        elif not text.get("0.0", END).strip():
            showerror("Ошибка", "Укажите содержимое заметки")
        else:
            if args:
                cur.execute("UPDATE notes SET name = ?, content = ? WHERE id = ?", (entry.get(), text.get("0.0", END), id))
            else:
                cur.execute("INSERT INTO notes (name, content) VALUES (?, ?)", (entry.get(), text.get("0.0", END)))
            db.commit()
            update_func()
            window.destroy()

    def cancel(*args):
        window.destroy()

    Label(window, text="Название:").place(relheight=0.05, relx=0.05, rely=0.05, relwidth=0.2)
    Label(window, text="Содержимое:").place(relheight=0.05, relwidth=0.2, relx=0.4, rely=0.15)

    entry = Entry(window)
    entry.place(relheight=0.05, relx=0.3, rely=0.05, relwidth=0.65)

    text = Text(window, wrap=WORD)
    text.place(relwidth=0.9, relx=0.05, rely=0.25, relheight=0.6)

    if args:
        entry.insert(0, name)
        text.insert("0.0", content)

    button_save = Button(window, text="Сохранить", relief=SOLID, command=save)
    button_save.place(relheight=0.05, relwidth=0.3, rely=0.9, relx=0.05)
    window.bind("<Control-s>", save)

    button_cancel = Button(window, text="Отмена", relief=SOLID, command=cancel)
    button_cancel.place(relheight=0.05, relwidth=0.3, rely=0.9, relx=0.65)
    window.bind("<Escape>", cancel)

def delete(*args, update_func=None):
    global notes, notes_listbox

    select_note = notes[notes_listbox.curselection()[0]]

    result = askyesno(title=f"Удаление заметки \"{select_note[1]}\"",
                      message=f"Вы уверены, что хотите удалить заметку \"{select_note[1]}\"")

    if result:
        cur.execute("DELETE FROM notes WHERE id = ?", (select_note[0],))
        db.commit()

        showinfo("Заметка удалена", message=f"Заметка {select_note[1]} удалена навсегда")

        update_func()
        on_select()

def update():
    global notes, notes_var

    cur.execute("SELECT id, name FROM notes")
    notes = cur.fetchall()
    notes_var.set([note[1] for note in notes])


def get_index():
    global notes_listbox

    return notes_listbox.curselection()[0]


def on_select(*args):
    global button_edit, button_delete, notes_listbox

    if notes_listbox.curselection():
        button_edit.config(state=NORMAL)
        button_delete.config(state=NORMAL)
    else:
        button_edit.config(state=DISABLED)
        button_delete.config(state=DISABLED)

cur.execute("SELECT id, name FROM notes")
notes = cur.fetchall()

notes_var = Variable(value=[note[1] for note in notes])
notes_listbox = Listbox(root, listvariable=notes_var, selectmode=SINGLE)
notes_listbox.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.05)
notes_listbox.bind("<<ListboxSelect>>", on_select)
notes_listbox.bind("<Return>", lambda *args: note(notes[get_index()][0], update_func=update))
notes_listbox.bind("<Double-Button-1>", lambda *args: note(notes[get_index()][0], update_func=update))
notes_listbox.bind("<Delete>", lambda *args: delete(update_func=update))

button_edit = Button(root, text="Изменить", relief=SOLID, state=DISABLED, command=lambda : note(notes[get_index()][0], update_func=update))
button_edit.place(relheight=0.05, relwidth=0.3, rely=0.9, relx=0.05)

button_add = Button(root, text="Добавить", relief=SOLID, command=lambda : note(update_func=update))
button_add.place(relheight=0.05, relwidth=0.2, rely=0.9, relx=0.4)

button_delete = Button(root, text="Удалить", relief=SOLID, state=DISABLED, command=lambda : delete(update_func=update))
button_delete.place(relheight=0.05, relwidth=0.3, rely=0.9, relx=0.65)

root.mainloop()