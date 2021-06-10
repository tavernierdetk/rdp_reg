from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class SheetsUpdater:
    def __init__(self, sheet_id, tab_name):
        self.sheet_id = sheet_id
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.tab_name = tab_name
        self.values = []

    def update(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../JSONFiles/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()


        # The A1 notation of a range to search for a logical table of data.
        # Values will be appended after the last row of the table.
        range_ = self.tab_name + '!A2:C'

        # How the input data should be interpreted.
        value_input_option = 'USER_ENTERED'

        # How the input data should be inserted.
        insert_data_option = 'INSERT_ROWS'

        value_range_body = {

            "majorDimension": "ROWS",
            "values": self.values
        }
        request = service.spreadsheets().values().append(spreadsheetId=self.sheet_id, range=range_,
                                                         valueInputOption=value_input_option,
                                                         insertDataOption=insert_data_option, body=value_range_body)
        response = request.execute()

        print(response)


    def addDataPoint(self, datapoint):
        self.values.append(datapoint)

# The ID and range of a sample spreadsheet.



if __name__ == '__main__':
    SAMPLE_SPREADSHEET_ID = '1VGMlWxllRFoHYyKYqJIpUeQd3MdxwBDIVbI4TKyuIq4'
    tab_name = 'fb_posts'
    SAMPLE_UPDATE_DATA = pickle.load(open('fb_post.pickle', 'rb'))

    updater = SheetsUpdater(SAMPLE_SPREADSHEET_ID, tab_name)

    for post in SAMPLE_UPDATE_DATA:
        listed = [post[4], post[3], post[2], post[1]]
        updater.addDataPoint(listed)



    updater.update()