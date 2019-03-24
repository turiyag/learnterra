#!/usr/bin/env python

import datetime
import hashlib
import json
import os
import re
import sys
import time
from os.path import relpath
from tempfile import mkdtemp
from uuid import UUID
from zipfile import ZipFile, ZIP_DEFLATED

import arrow

# Use time.clock on Python < 3.3
high_res_timestamp_function = getattr(time, "perf_counter", time.clock)

initial_perf = high_res_timestamp_function()
initial_time = time.time()
perf_time_offset = initial_time - initial_perf


def precise_utcnow_arrow():
    """
    The normal datetime.utcnow() function has very wide granularity on some computers,
    this function is guaranteed to always generate sequential timestamps
    """
    global perf_time_offset
    timestamp_in_secs = high_res_timestamp_function() + perf_time_offset
    dt = datetime.datetime.utcfromtimestamp(timestamp_in_secs)
    return arrow.Arrow.fromdatetime(dt)


def timing(fn, print_output=True):
    """Times a given function"""
    start = precise_utcnow_arrow()
    fn()
    end = precise_utcnow_arrow()
    if print_output:
        print("Duration: {} - Start: {} - End: {}".format(end - start, start, end))
    return end - start, start, end


def generate_file_sha1(fetch_file_path, blocksize=2 ** 16):
    m = hashlib.sha1()
    with open(fetch_file_path, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def basic_utc_timestamp(high_resolution=False):
    if high_resolution:
        return arrow.utcnow().format("YYYY-MM-DDTHH-mm-ss.SSS") + "Z"
    else:
        return arrow.utcnow().format("YYYY-MM-DDTHH-mm-ss") + "Z"


def proper_utc_timestamp():
    return arrow.utcnow().isoformat()


class BetterJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, arrow.Arrow):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if hasattr(obj, "toJSON"):
            return obj.toJSON()
        if hasattr(obj, "to_json"):
            return obj.to_json()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def pretty_json(obj):
    return json.dumps(obj, indent=2, cls=BetterJSONEncoder)


def pretty_json_print(obj):
    print(pretty_json(obj))


def log(msg, *args, **kwargs):
    utc_timestamp = proper_utc_timestamp()
    if not isinstance(msg, list) and not isinstance(msg, dict):
        print("[%s]: %s" % (utc_timestamp, msg), *args, **kwargs)
    else:
        json_text = pretty_json(msg)
        for line in json_text.split("\n"):
            print("[%s]: %s" % (utc_timestamp, line), *args, **kwargs)
    sys.stdout.flush()


def flatten(structured_data):
    # Assume that we are passed a dictionary unconditionally
    flat_data = {}
    for (key, value) in structured_data.items():
        if not isinstance(value, list) and not isinstance(value, dict):
            flat_data[key] = value
        else:
            if isinstance(value, dict):
                flattened = flatten(value)
            else:
                dict_form = {}
                for (index, item) in enumerate(value):
                    dict_form["%s" % index] = item
                flattened = flatten(dict_form)
            for (subkey, subvalue) in flattened.items():
                flat_data["%s_%s" % (key, subkey)] = subvalue
    return flat_data


def save_json(data, json_path):
    with open(json_path, "w") as outfile:
        json.dump(data, outfile, indent=2, cls=BetterJSONEncoder)


def load_json(json_path):
    with open(json_path, "r") as json_file:
        return json.load(json_file)


def save_properties(data, props_path):
    props_data = flatten(data)
    with open(props_path, "w") as outfile:
        for (key, value) in props_data.items():
            outfile.write("_%s=%s\n" % (key.upper(), value))


def save_json_and_properties(data, dir_path, filename_prefix):
    json_path = os.path.join(dir_path, filename_prefix + ".json")
    save_json(data, json_path)

    props_path = os.path.join(dir_path, filename_prefix + ".properties")
    save_properties(data, props_path)


def zip_dir(zip_path, dir_path):
    uncompressed_size = 0
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as myzip:
        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                arcpath = relpath(filepath, dir_path)
                uncompressed_size += os.stat(filepath).st_size
                myzip.write(filepath, arcpath)
    return zip_path, uncompressed_size


def tmp_zip_dir(zip_name, dir_path):
    temp_dir = mkdtemp()
    zip_path = os.path.join(temp_dir, zip_name)
    return zip_dir(zip_path, dir_path)


def valid_timestamped_filename_checker(filename, template_regex):
    main_match = re.match(template_regex, filename, re.IGNORECASE)

    if main_match:
        date_dict = main_match.groupdict()
        if "YY" in date_dict:
            datestring = "{YY}-{MM}-{DD}".format(**date_dict)
            try:
                return arrow.get(datestring, "YY-MM-DD")
            except ValueError:
                return False
        elif "HH" in date_dict:
            datestring = "{YYYY}-{MM}-{DD}T{HH}:{mm}:{ss}".format(**date_dict)
            try:
                return arrow.get(datestring, "YYYY-MM-DDTHH:mm:ss")
            except ValueError:
                return False
        elif "MMM" in date_dict:
            datestring = "{DD}-{MMM}-{YYYY}".format(**date_dict)
            try:
                return arrow.get(datestring, "DD-MMM-YYYY")
            except ValueError:
                return False
        elif "YYYY" in date_dict:
            datestring = "{YYYY}-{MM}-{DD}".format(**date_dict)
            try:
                return arrow.get(datestring, "YYYY-MM-DD")
            except ValueError:
                return False
        else:
            return arrow.get()
    else:
        return False
