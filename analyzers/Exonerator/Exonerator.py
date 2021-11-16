#!/usr/bin/env python3
# encoding: utf-8

import requests
from datetime import date

from bs4 import BeautifulSoup
from cortexutils.analyzer import Analyzer


class ExoneratorAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.session = requests.Session()
        self.baseurl = 'https://metrics.torproject.org/exonerator.html'
        self.result = None

    def summary(self, raw):
        taxonomies = []
        level = "info"
        namespace = "Exonerator"
        predicate = "Result"
        value = self.result

        taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))
        return {"taxonomies": taxonomies}

    def query_data(self, ipaddr):
        """
        Example request ?ip=123.123.123.123&timestamp=2021-12-24&lang=en
        """
        response = None
        today = date.today().strftime("%Y-%m-%d")
        headers = {'Referer': self.baseurl,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/95.0.4638.69 Safari/537.36'}
        params = {'ip': ipaddr, 'timestamp': today, 'lang': 'en'}

        try:
            response = self.session.get(self.baseurl, params=params, headers=headers)
        except (requests.ConnectionError, requests.HTTPError) as er:
            self.error("Error fetching data. Error: {}".format(er))
        return response

    def parse_data(self, response):
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            result = soup.select('h3.panel-title')[0].text.strip()
            return result
        except Exception as e:
            self.error("Beautifulsoap error: {}".format(e))

    def run(self):
        response = None
        if self.data_type == 'ip':
            ipaddr = self.get_param('data', None, 'Observable is missing')
            try:
                response = self.query_data(ipaddr)
                if response is None or response.status_code != 200:
                    self.error("Unexpected status code from. Status code: {}".format(response.status_code))
            except Exception as e:
                self.unexpectedError(e)
        else:
            self.error("Data type not supported!")

        self.result = self.parse_data(response)


if __name__ == '__main__':
    ExoneratorAnalyzer().run()