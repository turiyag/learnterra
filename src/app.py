#!/usr/bin/env python

"""
Run Flask Site
Examples:
    # Run on port 8080
    ./app.py --port 8080
    
"""

from argparse import RawDescriptionHelpFormatter, ArgumentParser

import arrow
from flask import Flask

from util import pretty_json

EPILOG = __doc__

application = Flask(__name__)


def better_jsonify(obj):
    return application.response_class(pretty_json(obj), mimetype=application.config["JSONIFY_MIMETYPE"])


def as_json(func):
    def as_json_wrapper():
        return better_jsonify(func())

    return as_json_wrapper


@application.route("/")
def hello():
    return better_jsonify({"msg": "Hello World!!!", "now": arrow.get()})


@application.route("/x")
@as_json
def x():
    return {"x": "Hello World!!!", "now": arrow.get()}


def main(port=8080):
    application.run(port=port)


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=EPILOG, description="Run Flask Site")
    parser.add_argument("--port", help="The TCP port to listen on", type=str, default=8080)
    parsed_arguments = parser.parse_args()
    main(parsed_arguments.port)
