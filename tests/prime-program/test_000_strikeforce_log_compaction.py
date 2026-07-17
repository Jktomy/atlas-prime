from __future__ import annotations

"""Temporary Strikeforce diagnostic: compact unittest success output only.

This module changes no assertions, test ordering, pass/fail semantics, or exit codes.
It is intentionally removed before the final accepted PR head.
"""

import unittest


def _quiet_start_test(self: unittest.TextTestResult, test: unittest.case.TestCase) -> None:
    unittest.TestResult.startTest(self, test)


def _quiet_success(self: unittest.TextTestResult, test: unittest.case.TestCase) -> None:
    unittest.TestResult.addSuccess(self, test)


def _quiet_skip(self: unittest.TextTestResult, test: unittest.case.TestCase, reason: str) -> None:
    unittest.TestResult.addSkip(self, test, reason)


def _quiet_expected_failure(
    self: unittest.TextTestResult,
    test: unittest.case.TestCase,
    err: tuple[type[BaseException], BaseException, object],
) -> None:
    unittest.TestResult.addExpectedFailure(self, test, err)


def _quiet_unexpected_success(self: unittest.TextTestResult, test: unittest.case.TestCase) -> None:
    unittest.TestResult.addUnexpectedSuccess(self, test)


unittest.TextTestResult.startTest = _quiet_start_test
unittest.TextTestResult.addSuccess = _quiet_success
unittest.TextTestResult.addSkip = _quiet_skip
unittest.TextTestResult.addExpectedFailure = _quiet_expected_failure
unittest.TextTestResult.addUnexpectedSuccess = _quiet_unexpected_success
