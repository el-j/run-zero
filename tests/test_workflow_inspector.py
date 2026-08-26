"""
Unit tests for the dependency-free workflow-YAML services/container detector.
"""

import unittest

from workflow_inspector import job_uses_services_or_container

CI_YML = """\
jobs:
  api-build:
    name: API — Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

  api-test:
    name: API — Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        ports:
          - 40432:5432
    steps:
      - name: Apply database migrations
        run: psql -h localhost -p 40432
      - name: Tests
        run: go test ./...

  api-lint:
    name: API — Lint
    runs-on: ubuntu-latest
    steps:
      - uses: golangci/golangci-lint-action@v9
"""

CONTAINER_JOB_YML = """\
jobs:
  build-in-container:
    name: Build In Container
    container: node:24
    steps:
      - run: npm run build
"""

SERVICES_BEFORE_NAME_YML = """\
jobs:
  weird-order:
    services:
      redis:
        image: redis:7
    name: Weird Order
    steps:
      - run: echo hi
"""


class TestWorkflowInspector(unittest.TestCase):
    def test_job_with_services_block_detected(self):
        self.assertTrue(job_uses_services_or_container(CI_YML, "API — Tests"))

    def test_job_without_services_block_is_false(self):
        self.assertFalse(job_uses_services_or_container(CI_YML, "API — Lint"))
        self.assertFalse(job_uses_services_or_container(CI_YML, "API — Build"))

    def test_container_key_also_counts(self):
        self.assertTrue(job_uses_services_or_container(CONTAINER_JOB_YML, "Build In Container"))

    def test_services_declared_before_name_key_still_detected(self):
        self.assertTrue(job_uses_services_or_container(SERVICES_BEFORE_NAME_YML, "Weird Order"))

    def test_unknown_job_name_returns_none(self):
        self.assertIsNone(job_uses_services_or_container(CI_YML, "Nonexistent Job"))

    def test_empty_inputs_return_none(self):
        self.assertIsNone(job_uses_services_or_container("", "API — Tests"))
        self.assertIsNone(job_uses_services_or_container(CI_YML, ""))
        self.assertIsNone(job_uses_services_or_container(None, "API — Tests"))

    def test_step_level_name_is_not_mistaken_for_job_name(self):
        # "Apply database migrations" and "Tests" are STEP names (list items,
        # "- name: ..."), not job names -- must not match at all.
        self.assertIsNone(job_uses_services_or_container(CI_YML, "Apply database migrations"))

    def test_quoted_job_name_matches(self):
        text = 'jobs:\n  x:\n    name: "Quoted Name"\n    services:\n      db:\n        image: postgres\n'
        self.assertTrue(job_uses_services_or_container(text, "Quoted Name"))


if __name__ == "__main__":
    unittest.main()
