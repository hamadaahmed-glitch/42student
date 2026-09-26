"""
Unit tests for raw error pattern categorization.
"""

from __future__ import annotations

from student42.analytics.mistake_tracker import MistakeClassifier


def test_segfault_classification():
    err = "Program terminated with signal SIGSEGV, Segmentation fault."
    assert MistakeClassifier.classify(err) == "memory_segmentation_fault"


def test_valgrind_leak_classification():
    err = "LEAK SUMMARY: definitely lost: 128 bytes in 1 blocks"
    assert MistakeClassifier.classify(err) == "memory_leak"


def test_norminette_line_count_classification():
    err = "Error: TOO_MANY_LINES (line:  26, col:   1): Function has more than 25 lines"
    assert MistakeClassifier.classify(err) == "norm_function_length"


def test_syntax_classification():
    err = "ft_strlen.c:12:5: error: expected ';' before 'return'"
    assert MistakeClassifier.classify(err) == "compiler_syntax"