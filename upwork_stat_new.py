import upwork
import datetime
import re


def get_last_week_date_query():
    today = datetime.date.today()
    weekday = today.weekday()
    last_week_delta = datetime.timedelta(days=weekday, weeks=3)
    start_of_last_week = today - last_week_delta
    end_of_last_week = start_of_last_week + datetime.timedelta(days=6)
    return "date >= {} AND date <= {}".format(start_of_last_week.__str__(), end_of_last_week.__str__())


class UpworkFinanceReporter:
    def __init__(self):
        self.public_key = "6978f9b2878abedfac958c5f4a786bc4"
        self.secret_key = "b2d54278ad940934"
        self.provider_id = '1077270'
        self.tokens_filename = "access_tokens"
        self.load_tokens()

    def load_tokens(self):
        try:
            self.client = self.saved_access_client(open(self.tokens_filename, 'r'))
        except:
            self.client = self.create_new_client(open(self.tokens_filename, 'w'))

    def saved_access_client(self, token_file):
        tokens = token_file.read().split("\n")
        oauth_access_token, oauth_access_token_secret = tokens[0], tokens[1]
        client = upwork.Client(self.public_key, self.secret_key,
                               oauth_access_token=oauth_access_token,
                               oauth_access_token_secret=oauth_access_token_secret)
        return client

    def create_new_client(self, token_file):
        client = upwork.Client(self.public_key, self.secret_key)

        print "Please to this URL (authorize the app if necessary):"
        print client.auth.get_authorize_url()
        print "After that you should be redirected back to your app URL with " + \
              "additional ?oauth_verifier= parameter"

        verifier = raw_input('Enter oauth_verifier: ')

        oauth_access_token, oauth_access_token_secret = \
            client.auth.get_access_token(verifier)
        token_file.write(oauth_access_token + "\n" + oauth_access_token_secret)

        client = upwork.Client(self.public_key, self.secret_key,
                               oauth_access_token=oauth_access_token,
                               oauth_access_token_secret=oauth_access_token_secret)
        return client

    def count_report(self, report):
        key_value_row = list(report.get("table").get("rows"))
        summary_expense = 0
        for item in key_value_row:
            transaction_value = float(item.get('c').get('v'))
            if transaction_value < 0:
                summary_expense -= transaction_value
        return summary_expense

    def get_financial_report(self):
        try:
            date = get_last_week_date_query()
            print "Get financial reports for the current user's account; DATE = " + date
            query = "SELECT amount WHERE " + date
            report = self.client.finreport.get_financial_entities_provider(self.provider_id, query)
            return str(self.count_report(report))
        except Exception, e:
            print "Exception at %s %s" % (self.client.last_method, self.client.last_url)
            raise e


