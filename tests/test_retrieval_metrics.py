from src.evaluation.metrics import hit_at_k, reciprocal_rank


def make_result(source_path: str) -> dict:
    return {
        "source_path": source_path,
    }


def test_hit_at_k() -> None:
    results = [
        make_result("wrong.md"),
        make_result("target.md"),
        make_result("other.md"),
    ]

    assert hit_at_k(
        results,
        ["target.md"],
        1,
    ) == 0

    assert hit_at_k(
        results,
        ["target.md"],
        3,
    ) == 1


def test_reciprocal_rank() -> None:
    results = [
        make_result("wrong.md"),
        make_result("target.md"),
    ]

    assert reciprocal_rank(
        results,
        ["target.md"],
    ) == 0.5


def test_missing_source_has_zero_reciprocal_rank() -> None:
    results = [
        make_result("wrong.md"),
    ]

    assert reciprocal_rank(
        results,
        ["target.md"],
    ) == 0.0