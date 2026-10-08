def hit_at_k(
    results: list[dict],
    expected_source_files: list[str],
    k: int,
) -> int:
    expected = set(expected_source_files)

    return int(
        any(
            result.get("source_path") in expected
            for result in results[:k]
        )
    )


def reciprocal_rank(
    results: list[dict],
    expected_source_files: list[str],
) -> float:
    expected = set(expected_source_files)

    for rank, result in enumerate(results, start=1):
        if result.get("source_path") in expected:
            return 1.0 / rank

    return 0.0