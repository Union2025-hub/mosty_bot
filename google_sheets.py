import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_sheet(user_id, username, text):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('gdrive_token.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Zayavki Yalta_bot").sheet1
    sheet.append_row([user_id, username, text])
