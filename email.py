import imaplib
import email
import os
import tkinter as tk


# функция для извлечения текста сообщения
def extract_text(payload):
    if isinstance(payload, str):
        return payload
    elif isinstance(payload, bytes):
        return str(payload, "utf-8", errors="ignore")
    else:
        return ""


# функция для проверки, является ли вложение JavaScript-файлом
def check_attachment(part):
    content_type = part.get_content_type()
    filename = part.get_filename()
    if content_type == "application/javascript" or (
        filename and filename.endswith(".js")
    ):
        return True
    return False


# функция для проверки, содержит ли сообщение JavaScript-код
def check_message(message):
    javascript_found = False
    for part in message.walk():
        content_type = part.get_content_type()
        if content_type == "text/plain" or content_type == "text/html":
            text = extract_text(part.get_payload())
            if "text/javascript" in text:
                javascript_found = True
        elif content_type == "application/octet-stream":
            if check_attachment(part):
                javascript_found = True
        elif content_type == "multipart/mixed":
            for subpart in part.get_payload():
                if (
                    subpart.get_content_type() == "application/octet-stream"
                    and check_attachment(subpart)
                ):
                    javascript_found = True
    return javascript_found


# функция для обработки нажатия кнопки поиска сообщений
def search_messages():
    imap_server = server_entry.get()
    imap_user = user_entry.get()
    imap_password = password_entry.get()
    imap_folder = folder_entry.get()

    # подключение к серверу
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(imap_user, imap_password)
    imap.select(imap_folder)

    # поиск сообщений, содержащих JavaScript-код
    response, messages = imap.search(None, "BODY", "javascript")
    if messages:
        for message in messages[0].split():
            response, data = imap.fetch(message, "(RFC822)")
            email_message = email.message_from_bytes(data[0][1])
            if check_message(email_message):
                result_text.insert(
                    tk.END,
                    f"Found JavaScript code in message {email_message['Subject']}\n",
                )
    else:
        result_text.insert(tk.END, "No messages with JavaScript code found\n")

    # отключение от сервера
    imap.close()
    imap.logout()


# создание главного окна
root = tk.Tk()
root.title("Поиск JS в письмах")

# создание виджетов для ввода параметров подключения к почтовому серверу
server_label = tk.Label(root, text="IMAP server:")
server_label.pack()
server_entry = tk.Entry(root)
server_entry.pack()

user_label = tk.Label(root, text="Username:")
user_label.pack()
user_entry = tk.Entry(root)
user_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

folder_label = tk.Label(root, text="IMAP folder:")
folder_label.pack()
folder_entry = tk.Entry(root)
folder_entry.pack()

search_button = tk.Button(root, text="Search", command=search_messages)
search_button.pack()

result_label = tk.Label(root, text="Search results:")
result_label.pack()
result_text = tk.Text(root)
result_text.pack()


# root.geometry("400x200")
# костыль
def close_window():
    root.destroy()
    root.quit()
    os._exit(0)


root.protocol("WM_DELETE_WINDOW", close_window)

# стартуем
root.mainloop()
