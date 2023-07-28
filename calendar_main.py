from __future__ import print_function
import datetime
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


# Без сервис аккаунта
# def join_calendar():
#     SCOPES = ['https://www.googleapis.com/auth/calendar']
#
#     creds = None
#
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('tomamanikur_OAuth.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     try:
#         service = build('calendar', 'v3', credentials=creds)
#     except HttpError as error:
#         print('An error occurred: %s' % error)
#     return(service)

# С сервис аккаунтом
class GoogleCalendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    FILE_PATH = 'service_account.json'
    calendar_id = '474cb7ebb4963c370299016e30fda69ac51ef18cbbbd54108f2db4377285f05d@group.calendar.google.com'
    min_hour = '10:00'
    max_hour = '23:00'
    dlitelnost = 4

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH, scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }

        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def show_events(self, calendar_id):

        try:
            # calendarId = 'primary'

            # время по МСК
            now = (datetime.datetime.utcnow() + timedelta(hours=3)).isoformat() + 'Z'

            events_result = self.service.events().list(calendarId=calendar_id, timeMin=now,
                                                  maxResults=100, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                zavtra = datetime.datetime.utcnow() + timedelta(hours=3) + timedelta(days=1)
                #фейковое событие если нет других
                events = [{
                  'summary': 'Маникюр',
                  'description':'Имя: Xxxx   Телеграмм: Yyyy   chat_id: 000000 id',
                  'start': {
                    'dateTime': str(zavtra.date())+'T01:00:00+03:00'
                  },
                  'end': {
                    'dateTime': str(zavtra.date())+'T02:00:00+03:00'
                  }
                }]
            else:
                pass


            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                #print(start, end, event['summary'])

        except HttpError as error:
            print('An error occurred: %s' % error)

        return events

    def show_events_date(self, calendar_id):
        sevodnya = datetime.datetime.utcnow() + timedelta(hours=3)
        sevodnya_min = str(sevodnya.date()) + 'T00:00:00+03:00'
        sevodnya_max = str(sevodnya.date()) + 'T23:00:00+03:00'

        events_result = self.service.events().list(calendarId=calendar_id, timeMin=sevodnya_min,timeMax=sevodnya_max,
                                                   maxResults=100, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
    def add_event(self, calendar_id, event):
        # event = {
        #   'summary': 'Маникюр',
        #   'location': '800 Howard St., San Francisco, CA 94103',
        #   'description': 'A chance to hear more about Google\'s developer products.',
        #   'start': {
        #     'dateTime': '2023-07-01T09:00:00+03:00',
        #   },
        #   'end': {
        #     'dateTime': '2023-07-01T13:00:00+03:00',
        #   }
        # }
        self.service.events().insert(calendarId=calendar_id, body=event).execute()
        print('Добавлено событие \n', event['summary'])

    def dell_event(self, calendar_id, eventId):
        self.service.events().delete(calendarId=calendar_id, eventId=eventId).execute()
        print('Удалено событие \n', eventId)


    def perdelta(self, start, end, delta):
        curr = start
        while curr < end:
            yield curr
            curr += delta
    def str_to_datetime(self, str):
        str = datetime.datetime.strptime(str, "%Y-%m-%dT%H:%M:%S+03:00")
        return str

    #устарело
    # def days_to_zapis(self):
    #     days_zapis_14_days = []
    #     now = datetime.datetime.utcnow() + timedelta(hours=3)
    #     for i in range(14):
    #         days_zapis_14_days.append(str(now.date() + timedelta(days=i)))
    #     return days_zapis_14_days

    def time_to_zapis_all(self):
        days = 14
        start_time = '10:00'
        end_time = '23:00'
        last_hour = int(end_time.split(':')[0])
        last_minute = int(end_time.split(':')[1])

        start = datetime.datetime.utcnow() + timedelta(hours=3)
        start = start - timedelta(minutes=start.minute % 30,
                                  seconds=start.second,
                                  microseconds=start.microsecond) + timedelta(minutes=30)
        end = start + timedelta(days=days)
        end = end.replace(hour=last_hour, minute=last_minute)

        time_zapis_14_days = {}
        for result in self.perdelta(start, end, timedelta(minutes=30)):
            if result.time() in self.vozmojnoe_vremya_priema(start_time, end_time):
                if result.date() in time_zapis_14_days:
                    time_zapis_14_days[result.date()].append(result.time())
                else:
                    a = []
                    a.append(result.time())
                    time_zapis_14_days[result.date()] = a
        return (time_zapis_14_days)

    def vozmojnoe_vremya_priema(self,start,end):
        open_time = ['2023-06-28T{0}:00+03:00'.format(start), '2023-06-28T{0}:00+03:00'.format(end)]
        free_time = []

        for result in self.perdelta(self.str_to_datetime(open_time[0]), self.str_to_datetime(open_time[1]), timedelta(minutes=30)):
            free_time.append(result.time())
        return free_time

    def not_free_date(self, calendar_id):
        now = (datetime.datetime.utcnow() + timedelta(hours=3)).isoformat() + 'Z'
        events = self.show_events(calendar_id)

        zanatoe_sobitie = []
        for event in events:
            #print(event)
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            zapis = [start, end]
            zanatoe_sobitie.append(zapis)

        zanatoe_vremya = {}
        for date in zanatoe_sobitie:
            for result in self.perdelta(self.str_to_datetime(date[0]), self.str_to_datetime(date[1]), timedelta(minutes=30)):
                if result.date() in zanatoe_vremya:
                    zanatoe_vremya[result.date()].append(result.time())
                else:
                    a = []
                    a.append(result.time())
                    zanatoe_vremya[result.date()] = a

        return zanatoe_vremya

    def free_date_time(self, calendar_id):
        days_zapis_14_days = self.time_to_zapis_all()
        zanatoe_vremya = self.not_free_date(calendar_id)

        dop_plata_hour = [19, 20]

        free_dates = {}
        for day in days_zapis_14_days:
            if day in zanatoe_vremya:
                free_dates[str(day)] = list(set(days_zapis_14_days[day]) - set(zanatoe_vremya[day]))
            else:
                free_dates[str(day)] = days_zapis_14_days[day]

        return(free_dates)

    def timedelta_to_datetime(self, td):
        dt = datetime.datetime.now()
        ordinal = dt.toordinal()
        new_dt = datetime.datetime.fromordinal(ordinal + td.days) + timedelta(seconds=td.seconds, microseconds=td.microseconds)
        return new_dt


    def date_time_dlya_zapisi(self, calendar_id, dlitelnost):
        free_dates = self.free_date_time(calendar_id)
        mesto_dlya_zapisi = {}
        for date in free_dates:
            for time in free_dates[date]:

                start = timedelta(hours=time.hour, minutes=time.minute)
                end = timedelta(hours=time.hour, minutes=time.minute) + timedelta(hours=dlitelnost)

                start = self.timedelta_to_datetime(start)
                end = self.timedelta_to_datetime(end)

                zanyatie_list = []
                for zanyatie in self.perdelta(start,end, timedelta(minutes=30)):
                    zanyatie_list.append(zanyatie.time())

                def check_if_sublist_within_list(sublist, larger_list):
                    return all(element in larger_list for element in sublist)

                result = check_if_sublist_within_list(zanyatie_list, free_dates[date])

                if result and date in mesto_dlya_zapisi:
                    mesto_dlya_zapisi[date].append(time)
                elif result:
                    a = []
                    a.append(time)
                    mesto_dlya_zapisi[date] = a
        return mesto_dlya_zapisi



    def free_date_pro(self, calendar_id):
        # Длительность услуги
        dlitelnost_manikyr = 4
        interval_dates = 30
        kol_vo_intervalov =[]

        free_dates = self.free_date_time(calendar_id)
        print(free_dates['2023-06-28'])
        print(sorted(free_dates['2023-06-28']))

    def id_show_events(self, calendar_id, chat_id):
        event_list = self.show_events(calendar_id)
        events = []
        for event in event_list:
            try:
                if event['description'].split('chat_id: ')[1] == chat_id:
                    events.append(event)
            except:
                pass
        return events

    def event_zavtra(self, calendar_id):
        event_list = self.show_events(calendar_id)
        event_zavtra = []
        zavta_date = (datetime.datetime.utcnow() + timedelta(hours=3) + timedelta(days=1)).date()
        for event in event_list:
            if str(zavta_date) == event['start']['dateTime'].split('T')[0]:
                event_zavtra.append(event)
        return event_zavtra

    def rassilka(self,calendar_id):
        event_zavtra = self.event_zavtra(calendar_id)
        event_zavtra_list = []
        for event in event_zavtra:
            # 'description': 'Имя: Михаил  Телеграмм: Venage  chat_id: 528287360'
            name_telegram_chatid = event['description'].split('  ')
            event_dict = {'Процедура':event['summary'],
                          'Имя': name_telegram_chatid[0].split(' ')[1],
                          'time': event['start']['dateTime'].split('T')[1].replace(':00+03:00',''),
                          'chat_id': name_telegram_chatid[2].split(' ')[1],
                          }
            event_zavtra_list.append(event_dict)
        return event_zavtra_list

    # def start_end_events(self, calendar_id):
    #     events = obj.show_events(calendar_id)
    #
    #     zanatoe_sobitie = {}
    #     date = []
    #     start_event_time = []
    #     end_event_time = []
    #     end_event_time = []
    #     id_event = []
    #     creator_event = []
    #     info = []
    #     for event in events:
    #
    #         # date = self.str_to_datetime(event['start'].get('dateTime', event['start'].get('date'))).date()
    #         # start_event_time = self.str_to_datetime(event['start'].get('dateTime', event['start'].get('date'))).time()
    #         # end_event_time = self.str_to_datetime(event['end'].get('dateTime', event['end'].get('date'))).time()
    #         # id_event = event['id']
    #         # creator_event = event['creator']
    #
    #         date.append(self.str_to_datetime(event['start'].get('dateTime', event['start'].get('date'))).date())
    #         start_event_time.append(self.str_to_datetime(event['start'].get('dateTime', event['start'].get('date'))))
    #         end_event_time.append(self.str_to_datetime(event['end'].get('dateTime', event['end'].get('date'))))
    #         id_event.append(event['id'])
    #         creator_event.append(event['creator'])
    #
    #     zanatoe_sobitie =\
    #         {
    #             'date':  date,
    #             'start_event_time': start_event_time,
    #             'end_event_time': end_event_time,
    #             'id_event': id_event,
    #             'creator_event': creator_event,
    #         }
    #     df_zanatoe_sobitie = pd.DataFrame(zanatoe_sobitie)
    #
    #     #df_zanatoe_sobitie['delta'] = df_zanatoe_sobitie['end_event_time'] - df_zanatoe_sobitie['start_event_time']
    #
    #     #print(df_zanatoe_sobitie)
    #     print(df_zanatoe_sobitie['start_event_time'][0])
    #     print(df_zanatoe_sobitie['end_event_time'][0])
    #     print(df_zanatoe_sobitie['end_event_time'][0] - df_zanatoe_sobitie['start_event_time'][0])
    #     print(type(df_zanatoe_sobitie['end_event_time'][0]))





if __name__ == '__main__':
    # Выполнять при добавлении календаря
    # obj.add_calendar(calendar_id='474cb7ebb4963c370299016e30fda69ac51ef18cbbbd54108f2db4377285f05d@group.calendar.google.com')
    obj = GoogleCalendar() # создание календаря для сервис аккаунта
    calendar_id = '474cb7ebb4963c370299016e30fda69ac51ef18cbbbd54108f2db4377285f05d@group.calendar.google.com'
    min_hour = '10:00'
    max_hour = '23:00'
    dlitelnost = 4

    event = {
        'summary': '🔹 Маникюр',
        'description': 'Имя: Михаил   Телеграмм: Venage   chat_id:528287360',
        'start': {
            'dateTime': '2023-07-02T09:00:00+03:00'},
        'end': {
            'dateTime': '2023-07-02T13:00:00+03:00'}
    }



    #print(obj.show_events_date(calendar_id))
    print(obj.event_zavtra(calendar_id))
    print(obj.rassilka(calendar_id))
    #print(obj.id_show_events(calendar_id, chat_id='528287360'))

    #obj.add_event(calendar_id,event)
    #obj.dell_event(calendar_id,'e8rt6ha9nbsapp146ilbnrsl88')
    #print(obj.time_to_zapis_all())
    #print(obj.vozmojnoe_vremya_priema(min_hour,max_hour))
    #print(obj.not_free_date(calendar_id))
    #print(obj.free_date_time(calendar_id))
    #print(obj.date_time_dlya_zapisi(calendar_id,dlitelnost))
    #obj.start_end_events(calendar_id)
    #obj.free_date_pro(calendar_id)






