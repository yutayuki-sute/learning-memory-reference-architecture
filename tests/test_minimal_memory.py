"""Conformance checks for the local toy example; no external accounts."""

import unittest

from examples.minimal_memory import PROJECT_MEMORY, process_request


class MinimalMemoryTests(unittest.TestCase):
    def test_retrieves_only_current_project_and_active_rows(self):
        result = process_request("DEMO", "workflow")
        self.assertEqual(result["retrieved"], ["Use small tests before changing a workflow."])
        self.assertEqual(result["gate"], "WRITEBACK_GATE")

    def test_no_candidate_means_no_writeback(self):
        ledger = []
        result = process_request("DEMO", "workflow", experience_log=ledger)
        self.assertEqual(result["writeback"], "SKIPPED")
        self.assertFalse(ledger)

    def test_no_evidence_means_no_writeback(self):
        ledger = []
        result = process_request("DEMO", "workflow", "New rule", experience_log=ledger)
        self.assertEqual(result["writeback"], "SKIPPED")
        self.assertFalse(ledger)

    def test_writeback_is_unreviewed_not_promoted(self):
        ledger = []
        result = process_request("DEMO", "workflow", "New rule", "DEMO-001", experience_log=ledger)
        self.assertEqual(result["writeback"], "APPENDED_UNREVIEWED")
        self.assertEqual(ledger[0]["review_status"], "UNREVIEWED")
        self.assertEqual(len(result["retrieved"]), 1)

    def test_duplicate_candidate_is_not_appended_again(self):
        ledger = []
        process_request("DEMO", "workflow", "  New  Rule ", "DEMO-001", experience_log=ledger)
        result = process_request("DEMO", "workflow", "new rule", "DEMO-002", experience_log=ledger)
        self.assertEqual(result["writeback"], "DUPLICATE")
        self.assertEqual(len(ledger), 1)

    def test_same_candidate_in_other_project_is_separate(self):
        ledger = []
        process_request("DEMO", "workflow", "New rule", "DEMO-001", experience_log=ledger)
        result = process_request("OTHER", "workflow", "New rule", "OTHER-001", experience_log=ledger)
        self.assertEqual(result["writeback"], "APPENDED_UNREVIEWED")
        self.assertEqual(len(ledger), 2)
        self.assertEqual(result["retrieved"], ["Never mix project notes."])

    def test_unknown_project_fails_closed(self):
        with self.assertRaises(ValueError):
            process_request("UNKNOWN", "workflow")

    def test_missing_gate_fails_closed(self):
        records = [row for row in PROJECT_MEMORY if row["key"] != "WRITEBACK_GATE"]
        with self.assertRaises(RuntimeError):
            process_request("DEMO", "workflow", memories=records)

    def test_duplicate_active_gate_fails_closed(self):
        gate = next(row for row in PROJECT_MEMORY if row["project_id"] == "DEMO")
        with self.assertRaises(RuntimeError):
            process_request("DEMO", "workflow", memories=PROJECT_MEMORY + [dict(gate)])


if __name__ == "__main__":
    unittest.main()
