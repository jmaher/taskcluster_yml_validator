# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import re

import jsone
import jsonschema
import pytest
import requests

import taskcluster_yml_validator
from taskcluster_yml_validator import validate

# Cache the schema download, so we don't hammer the TC instance
cache = {}


@pytest.fixture(autouse=True)
def cached_requests(monkeypatch):
    real_get = requests.get

    def get(url):
        if url not in cache:
            cache[url] = real_get(url)
        return cache[url]

    monkeypatch.setattr(taskcluster_yml_validator.requests, "get", get)


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_valid_taskcluster_yml():
    validate(os.path.join(FIXTURES_DIR, "bugbug.taskcluster.yml"))


def test_valid_taskcluster_yml_with_taskcluster_root_url_context():
    validate(os.path.join(FIXTURES_DIR, "task-boot.taskcluster.yml"))


def test_invalid_taskcluster_yml():
    with pytest.raises(
        jsone.shared.InterpreterError,
        match=re.escape(
            "InterpreterError at template.tasks[8].payload.command[2]: unknown context value tag"
        ),
    ):
        validate(os.path.join(FIXTURES_DIR, "bugbug_invalid.taskcluster.yml"))


def test_invalid_main_schema_taskcluster_yml():
    with pytest.raises(
        jsonschema.exceptions.ValidationError,
        match=re.escape("'version' is a required property"),
    ):
        validate(
            os.path.join(FIXTURES_DIR, "bugbug_invalid_main_schema.taskcluster.yml")
        )


def test_invalid_schema_taskcluster_yml():
    with pytest.raises(
        jsonschema.exceptions.ValidationError,
        match=re.escape("'metadata' is a required property"),
    ):
        validate(os.path.join(FIXTURES_DIR, "bugbug_invalid_schema.taskcluster.yml"))


def test_invalid_schema_payload_taskcluster_yml():
    with pytest.raises(
        jsonschema.exceptions.ValidationError,
        match=re.escape("'python3 run.py' is not of type 'array'"),
    ):
        validate(
            os.path.join(FIXTURES_DIR, "bugbug_invalid_schema_payload.taskcluster.yml")
        )


def test_invalid_schema_task_list_taskcluster_yml():
    with pytest.raises(
        TypeError,
        match=re.escape(
            "Task should be of dict type (after json-e parsing). Found: str"
        ),
    ):
        validate(
            os.path.join(
                FIXTURES_DIR, "bugbug_invalid_schema_task_list.taskcluster.yml"
            )
        )


def test_valid_taskcluster_yml_with_win_generic_worker():
    validate(os.path.join(FIXTURES_DIR, "win.taskcluster.yml"))


def test_valid_taskcluster_yml_with_no_tasks():
    validate(os.path.join(FIXTURES_DIR, "no_tasks_on_condition.taskcluster.yml"))
