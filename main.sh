#!/bin/bash
export FLASK_APP=$(dirname $0)/application.py
export FLASK_ENV=development
flask run