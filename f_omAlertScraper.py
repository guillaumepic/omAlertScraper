#!/usr/bin/env python
#
# Brief :
# Usage : See --help
#
# https://docs.opsmanager.mongodb.com/current/reference/api/alerts/
#
#
# GPI October 2021

''' Ops Manager alert scraper '''

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import requests
import yaml
from requests.auth import HTTPDigestAuth
from timeloop import Timeloop

__author__ = 'gpi'

# CONSTANTS
LOG = __file__ + " :: "
g_rootUrl = "/api/public/v1.0/"
g_sslMode = False
g_outputFile = ""

__version__ = "1.0"
g_periodicThread = Timeloop()


def f_print(log, verbose=False):
    if verbose:
        print(__file__ + " :: " + log)


def check_project(name, enpoint):
    '''Brief: Get project entry and unique id in the project list of the provided
    organization endpoint'''
    projects_r = False
    try:
        projects_r = requests.get("{0}".format(enpoint),
                                  auth=HTTPDigestAuth(str(args.pubKey),
                                                      str(args.privKey)),
                                  verify=g_sslMode)
        projects_r.raise_for_status()

    except requests.exceptions.RequestException as err:
        print(LOG + "Bad request", err)
    except requests.exceptions.HTTPError as errh:
        print(LOG + "Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print(LOG + "Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print(LOG + "Timeout Error:", errt)

    if projects_r:
        projects_j = projects_r.json()
        if (projects_j["name"] == g_argsSettings["ProjName"]):
            return True

    return False


def check_health():
    ''' Health Monitor'''
    health_r = False
    try:
        health_r = requests.get("{0}".format(g_baseUrl + "/monitor/health"),
                                auth=HTTPDigestAuth(str(args.pubKey),
                                                    str(args.privKey)),
                                verify=g_sslMode)
        health_r.raise_for_status()

    except requests.exceptions.RequestException as err:
        print(LOG + "Bad request", err)
    except requests.exceptions.HTTPError as errh:
        print(LOG + "Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print(LOG + "Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print(LOG + "Timeout Error:", errt)

    if health_r and health_r.json()["status"] == "OK":
        return True
    return False


def get_alerts(enpoint):
    '''Brief: Get project alerts '''

    alerts_default = {}
    if check_health():
        try:

            alerts_r = requests.get("{0}".format(enpoint + "/alerts/?status=OPEN"),
                                    auth=HTTPDigestAuth(str(args.pubKey),
                                                        str(args.privKey)),
                                    verify=g_sslMode)
            alerts_r.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(LOG + "Bad request", err)
        except requests.exceptions.HTTPError as errh:
            print(LOG + "Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print(LOG + "Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print(LOG + "Timeout Error:", errt)

        if alerts_r:
            return alerts_r.json()
    else:
        f_print("Health check Ops Manager failed ", g_verbose)
        alerts_default["results"] = [{"id": 0, "eventTypeName": "OM_HEALTH_CHECK", "date": str(datetime.utcnow()), "status": False}]
        return alerts_default


@g_periodicThread.job(interval=timedelta(seconds=5))
def collect_task():
    f_print("Periodic job current time : {}".format(str(datetime.utcnow())), g_verbose)
    alerts = get_alerts(g_projUrl)

    # Append JSON object to output file JSON array
    try:
        with open(g_outputFile, 'a+') as f_alerts:
            if not f_alerts.read(1) and os.stat(g_outputFile).st_size == 0:
                f_alerts.write("//## Alert collection file created {:%B %d, %Y},\n".format(datetime.now()))
                f_alerts.write("//## Ops Manager project : {0}\n".format(g_argsSettings["ProjName"]))

            for a in alerts["results"]:
                if a["id"] not in g_alerts_ids and a["id"] != 0:
                    g_alerts_ids.add(a["id"])
                    f_alerts.write(",")
                    f_alerts.write(json.dumps(a, separators=(',', ': '), indent=4))

                if a["id"] == 0:
                    f_alerts.write(",")
                    f_alerts.write(json.dumps(a, separators=(',', ': '), indent=4))

        with open(g_outputIdFile, 'w') as f_ids:
            for i in g_alerts_ids:
                # f_ids.write(i + " " + ",".join([str(x) for x in dict[i]]) + "\n")
                f_ids.write(i + ",\n")

    except Exception as e:
        f_print("ERROR: Flushing alerts objects in file", g_verbose)
        f_print("ERROR: Exception: " + str(e), g_verbose)


def f_init_alert_ids():
    '''Brief: Parse existing alerts objects and extract a set of alert ids '''
    res = True
    try:
        # with open(g_outputFile, 'r') as f_alerts:
        #     if f_alerts.read(1) and not os.stat(g_outputFile).st_size == 0:
        #         # f_strip_alerts = filter(lambda x: x.strip(), lines)
        #         # f_alerts.seek(0)
        #         j_alerts = json.load(f_alerts)
        #         f_print("INFO: Logged alerts loaded ")
        #         for a in j_alerts["id"]:
        #             f_print("Got an alert object id: " + a)
        #             g_alerts_ids.add(a)

        if not os.stat(g_outputIdFile).st_size == 0:
            with open(g_outputIdFile, 'r') as f_ids:
                for line in f_ids:
                    id_alert = line.split(",")
                    g_alerts_ids.add(str(id_alert[0]))
                f_print("INFO: Logged alerts loaded ")

    except Exception as e:
        f_print("ERROR: Parsing alerts file as json array", g_verbose)
        f_print("ERROR: Exception: " + str(e), g_verbose)
        res = False

    return res


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="http Ops Manager proxy rest-end point for scraping Alerts objects")
    required = parser.add_argument_group("Required arguments")
    required.add_argument("--url",
                          help="Ops Manager base url",
                          required=True)
    required.add_argument("--pubKey", help="OpsManager user public key",
                          required=True)
    required.add_argument("--privKey", help="API key to use", required=True)
    required.add_argument("--cfg", help="Configuration yaml file",
                          required=True,
                          default="f_omAlertScraper.yml")
    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument("--verbose", help="Enable stdout printing of logs",
                          action="store_false")
    args = parser.parse_args()
    # g_argsSettings: Dict[str, Union[Union[List[Any], bool], Any]] = {}
    g_argsSettings = {}

    g_verbose = args.verbose
    if args.cfg:
        f_print("Configuration file found " + str(args.cfg), g_verbose)
        if os.path.exists(args.cfg) is False:
            f_print("WARNING yaml configuration file is not found : " + args.cfg, g_verbose)
            sys.exit(0)

        cfg = yaml.safe_load(open(str(args.cfg)))
        g_argsSettings["ProjID"] = cfg["topology"]["projectId"]
        g_argsSettings["ProjName"] = cfg["topology"]["projectName"]
        if cfg["link"]["sslMode"]:
            g_sslMode = cfg["link"]["sslMode"]
            if g_sslMode:
                g_sslMode = cfg["link"]["sslCAFile"]
                if os.path.exists(g_sslMode) is False:
                    f_print("ERROR: CA pem file path is not found",
                            g_verbose)
                    sys.exit(0)

        if cfg["output"]["alert_filePath"] and cfg["output"]["id_filePath"]:
            g_outputFile = cfg["output"]["alert_filePath"]
            if os.path.exists(g_outputFile) is False:
                f_print("WARNING: output file is not found. Starting with a new list of alerts",
                        g_verbose)
            g_outputIdFile = cfg["output"]["id_filePath"]
            if os.path.exists(g_outputIdFile) is False:
                f_print("WARNING: identifier file is not found. Starting with a new list of alerts",
                        g_verbose)
        else:
            f_print("ERROR: output file path is undefined",
                    g_verbose)
            sys.exit(0)

        if cfg["param"]["period"]:
            g_argsSettings["period"] = cfg["param"]["period"]
        else:
            f_print("ERROR: scraping period is undefined",
                    g_verbose)
            sys.exit(0)
    else:
        f_print("Sorry yaml file not found !! ... ", g_verbose)
        sys.exit(1)

    # Endpoints
    g_baseUrl = str(args.url)
    g_rootUrl = g_baseUrl + g_rootUrl
    g_projUrl = g_rootUrl + "groups/" + str(g_argsSettings["ProjID"])

    # Check project exists
    if check_project(g_argsSettings["ProjName"], g_projUrl):
        f_print("Scraping alerts for Project: " + g_argsSettings["ProjName"], g_verbose)
        f_print("Detected alerts will be collected in output file: " + g_outputFile, g_verbose)
    else:
        f_print("ERROR no matching project found! Call someone ... ", g_verbose)
        sys.exit(1)

    # Init : Open outputfile, parse and list all alert ids
    g_alerts_ids = set()

    # Run : TimeLoop =>
    # - Get Alerts,
    # - Detect new alert ids
    # - Append newer alerts to outputfile
    if f_init_alert_ids():
        g_periodicThread.start(block=True)
    else:
        f_print("ERROR: Parsing alert file failure", g_verbose)

    f_print("bye ...", g_verbose)
    sys.exit(0)
