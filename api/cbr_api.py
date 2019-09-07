import xml.etree.ElementTree as ET

from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("CbrApi")

    def _update_rate(self, xrate):
        rate = self._get_cbr_rate(xrate.from_currency)
        return rate

    def _get_cbr_rate(self, from_currency):
        headers = {'User-Agent': 'YarikRulitYokoTop'}
        response = self._send_request(url="http://www.cbr.ru/scripts/XML_daily.asp", method="get", headers=headers)
        self.log.debug("response encoding: %s" % response.encoding)
        response_text = response.text
        self.log.debug("response.text: %s" % response_text)
        rate = self._find_rate(response_text, from_currency)

        return rate

    def _find_rate(self, response_text, from_currency):
        root = ET.fromstring(response_text)
        valutes = root.findall("Valute")

        cbr_valute_map = {840: "USD"}
        currency_cbr_alias = cbr_valute_map[from_currency]

        for valute in valutes:
            _new_val = valute.find("CharCode")
            if _new_val.text == currency_cbr_alias:
                return float(valute.find("Value").text.replace(",", "."))

        raise ValueError("Invalid CBR response")
