from __future__ import print_function

import os.path
import sys
from datetime import datetime

sys.path.append('./modules')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

import gspread
from gspread_dataframe import set_with_dataframe

import sqldb

mode = "PROD"

if mode == "TEST":
    bdb = sqldb.DB('BaseballTest.db')
else:
    bdb = sqldb.DB('Baseball.db')

# How tos:
# Bookmarks: HowTos / Dataviz / Tableau
# https://codesolid.com/google-sheets-in-python-and-pandas/
# https://console.cloud.google.com/apis/credentials?project=sheetspush&pli=1

def create(title):
    # """
    # Creates the Sheet the user has access to.
    # Load pre-authorized user credentials from the environment.
    # TODO(developer) - See https://developers.google.com/identity
    # for guides on implementing OAuth2 for the application.
    # #
    # File where credentials are stored
    # C:\Users\chery\AppData\Roaming\gspread\service_account.json
    # "client_email": "sheetspushsvcacct@sheetspush.iam.gserviceaccount.com"
    # This is the email address that the Google Sheet needs to recognize the data being sent to it
    # Add it to the list of accounts that can access the sheet using the "Share" button on the
    # top right corner of the Sheets page
    # ("USWS": https://docs.google.com/spreadsheets/d/1V6WC8etTn5GdgZsNzlsEaW7FI0c3uRWmPKl4h2ykBGA/edit#gid=0)
    # ("ESPN Rosters": https://docs.google.com/spreadsheets/d/1qsImcdcDSc0YNGwOoraN0Da0lLiaHtaQNGvz7NnzvzM/edit#gid=0 )
    # Standings_History_wOBA: 1d33gAPm8ygrHQNlxBuCD7nf7Tl7xqBcRtGfOdYz4Uhs
    # """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # pylint: disable=maybe-no-member
    try:
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId') \
            .execute()
        print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}\n\n"
              f"Add sheetspushsvcacct@sheetspush.iam.gserviceaccount.com to the Google Sheet to allow for updating")
        return spreadsheet.get('spreadsheetId')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def tables_to_sheets(table_name, worksheet_name):

    gc = gspread.service_account()
    gc.set_timeout(10)
    print(f'Opening {worksheet_name} {datetime.now().strftime("%Y%m%d-%H%M%S")}')
    try:
        sh = gc.open(worksheet_name)
        worksheet_title = "Sheet1"
        print(f'Opening {worksheet_title} {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        try:
            worksheet = sh.worksheet(worksheet_title)
            df_test = bdb.table_to_df(table_name)
            print(f'before {datetime.now().strftime("%Y%m%d-%H%M%S")}')
            set_with_dataframe(worksheet, df_test)
            print(f'after {datetime.now().strftime("%Y%m%d-%H%M%S")}')
        except gspread.WorksheetNotFound:
            print(f"Error in sh.worksheet {worksheet_title}")
            # worksheet = sh.add_worksheet(title=worksheet_title, rows=2500, cols=10)
    except gspread.SpreadsheetNotFound:
        print(f"error in gc.open {worksheet_name}. "
              f"Did you add sheetspushsvcacct@sheetspush.iam.gserviceaccount.com to the Google Sheet ?")
        #create(worksheet_name)
        #sh = gc.open(worksheet_name)


def main():
    try:
        #pass

        # create("SD_WOBA")
        # create("SD_WOBA_CURRENT")

        # tables_to_sheets("ESPNRosters","ESPNRosters")
        tables_to_sheets("UpcomingStartsWithStats","USWS")
        #tables_to_sheets("Standings_History_wOBA", "Standings_History_wOBA")

        # tables_to_sheets("SD_WOBA", "SD_WOBA")
        #tables_to_sheets("SD_WOBA_CURRENT", "SD_WOBA_CURRENT")

    except Exception as ex:
        print(str(ex))



if __name__ == '__main__':
    main()