"""
Unit tests for pedagogical reference access control.
"""

from __future__ import annotations

from student42.references.access_controller import AccessController, AccessMode


def test_strict_mode_blocks_uncompleted_work():
    assert not AccessController.can_view_reference(
        mode=AccessMode.STRICT,
        is_exercise_completed=False,
        is_explicitly_unlocked=False,
    )


def test_strict_mode_unlocked_after_completion():
    assert AccessController.can_view_reference(
        mode=AccessMode.STRICT,
        is_exercise_completed=True,
        is_explicitly_unlocked=False,
    )


def test_study_mode_masks_c_function_bodies():
    raw_c_code = (
        "#include <stddef.h>\n"
        "size_t ft_strlen(const char *s)\n"
        "{\n"
        "\tsize_t i = 0;\n"
        "\twhile (s[i])\n"
        "\t\ti++;\n"
        "\treturn (i);\n"
        "}\n"
    )

    masked = AccessController.filter_source_content(
        mode=AccessMode.STUDY,
        source_code=raw_c_code,
        is_completed=False,
    )

    assert "#include <stddef.h>" in masked
    assert "size_t ft_strlen(const char *s)" in masked
    assert "STUDY MODE: Implementation hidden" in masked
    assert "while (s[i])" not in masked