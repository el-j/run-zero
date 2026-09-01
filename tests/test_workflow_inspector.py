"""
Unit tests for the dependency-free workflow-YAML services/container detector.
"""

import unittest

from workflow_inspector import _iter_jobs, _looks_like_job_key, job_uses_services_or_container

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

UNNAMED_JOB_YML = """\
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
    steps:
      - run: pytest
"""

MATRIX_JOB_YML = """\
jobs:
  test:
    name: Test Matrix
    runs-on: ubuntu-latest
    strategy:
      matrix:
        py: ["3.10", "3.11"]
    services:
      redis:
        image: redis:7
    steps:
      - run: pytest
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

    def test_job_without_name_matches_by_job_id(self):
        self.assertTrue(job_uses_services_or_container(UNNAMED_JOB_YML, "integration-tests"))

    def test_matrix_expanded_job_name_matches_base_name(self):
        self.assertTrue(job_uses_services_or_container(MATRIX_JOB_YML, "Test Matrix (3.11)"))

    def test_iter_jobs_returns_empty_when_jobs_key_missing(self):
        self.assertEqual(list(_iter_jobs("name: only\n")), [])

    def test_iter_jobs_stops_when_top_level_dedents(self):
        text = """\
jobs:
  first:
    steps:
      - run: echo hi
name: workflow
"""
        jobs = list(_iter_jobs(text))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["job_id"], "first")

    def test_looks_like_job_key_rejects_invalid_lines(self):
        self.assertIsNone(_looks_like_job_key("", 2))
        self.assertIsNone(_looks_like_job_key("  # comment", 2))
        self.assertIsNone(_looks_like_job_key("first:", 2))
        self.assertIsNone(_looks_like_job_key("  - item:", 2))
        self.assertIsNone(_looks_like_job_key("  key", 2))
        self.assertIsNone(_looks_like_job_key("  invalid key:", 2))

    def test_iter_jobs_skips_non_job_entries_inside_jobs_block(self):
        text = """\
jobs:
  # comment in jobs block
  - not-a-job
  not_a_mapping
  valid-job:
    name: Valid Job
    steps:
      - run: echo hi
"""
        jobs = list(_iter_jobs(text))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["job_id"], "valid-job")


if __name__ == "__main__":
    unittest.main()
