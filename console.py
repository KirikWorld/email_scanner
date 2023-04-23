import imaplib
import email
import os


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
    imap_server = server_entry
    imap_user = user_entry
    imap_password = password_entry
    imap_folder = folder_entry

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
                result_text = f"Found JavaScript code in message {email_message['Subject']}\n"
                print(result_text)
                
    else:
        result_text = "No messages with JavaScript code found\n"
        print(result_text)

    # отключение от сервера
    imap.close()
    imap.logout()


server_entry = input("Imap server: ")
user_entry = input("username: ")
password_entry = input("password: ")
folder_entry = input("Imap folder: ")
search_messages()
