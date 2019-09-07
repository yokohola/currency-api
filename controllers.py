from flask import render_template, make_response, jsonify, request, redirect, url_for
import xmltodict
from models import XRate, ApiLog, ErrorLog
import api
from datetime import datetime
from app import app


class BaseController:
    def __init__(self):
        self.request = request

    def call(self, *args, **kwargs):
        try:
            return self._call(*args, **kwargs)
        except Exception as ex:
            return make_response(str(ex), 500)

    def _call(self, *args, **kwargs):
        raise NotImplementedError("_call")


class ViewAllRates(BaseController):
    def _call(self):
        xrates = XRate.select()
        return render_template("xrates.html", xrates=xrates)


class GetApiRates(BaseController):
    def _call(self, fmt):
        xrates = XRate.select()
        xrates = self._filter(xrates)

        if fmt == "json":
            return self._get_json(xrates)
        elif fmt == "xml":
            return self._get_xml(xrates)
        raise ValueError(f"Unknown format: {fmt}")

    def _filter(self, xrates):
        args = self.request.args

        if "from_currency" in args:
            xrates = xrates.where(XRate.from_currency == args.get("from_currency"))

        if "to_currency" in args:
            xrates = xrates.where(XRate.to_currency == args.get("to_currency"))

        return xrates

    def _get_xml(self, xrates):
        d = {
            "xrates":
                {
                 "xrate":
                     [
                         {
                             "from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate
                         } for rate in xrates
                     ]
                }
            }

        return make_response(xmltodict.unparse(d), {'Content-Type': 'text/xml'})

    def _get_json(self, xrates):
        return jsonify([{"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in xrates])


class UpdateRates(BaseController):
    def _call(self, from_currency, to_currency):
        if not from_currency and not to_currency:
            self._update_all()
        elif from_currency and to_currency:
            self._update_rate(from_currency, to_currency)
        else:
            raise ValueError("from_currency and to_currency")
        return redirect(url_for('view_rates'))

    def _update_rate(self, from_currency, to_currency):
        api.update_rate(from_currency, to_currency)

    def _update_all(self):
        xrates = XRate.select()
        for rate in xrates:
            print(rate)
            try:
                self._update_rate(rate.from_currency, rate.to_currency)
            except Exception as ex:
                app.logger.exception(ex)


class ViewLogs(BaseController):
    def _call(self, log_type):
        app.logger.debug("log_type: %s" % log_type)
        page = int(self.request.args.get("page", 1))
        logs_map = {"api": ApiLog, "error": ErrorLog}

        if log_type not in logs_map:
            raise ValueError("Unknown log_type: %s" % log_type)

        log_model = logs_map[log_type]
        logs = log_model.select().paginate(page, 10).order_by(log_model.id.desc())
        return render_template("logs.html", logs=logs)


class EditRate(BaseController):
    def _call(self, from_currency, to_currency):
        if self.request.method == "GET":
            return render_template("rate_edit.html", from_currency=from_currency, to_currency=to_currency)

        #POST REQUEST IS GOT
        print(request.form)
        if "new_rate" not in request.form:
            raise Exception("new_rate parametr is required")

        if not request.form["new_rate"]:
            raise Exception("new_rate must be not expty")

        upd_count = (XRate.update({XRate.rate: float(request.form["new_rate"]), XRate.updated: datetime.now()})
                     .where(XRate.from_currency == from_currency,
                            XRate.to_currency == to_currency).execute())

        print("upd_count", upd_count)
        return redirect(url_for('view_rates'))
