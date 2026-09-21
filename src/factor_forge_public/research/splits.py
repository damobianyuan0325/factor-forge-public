from __future__ import annotations

from pydantic import BaseModel, Field


class TimeSplit(BaseModel):
    train_start: int = Field(ge=0)
    train_end: int = Field(gt=0)
    test_start: int = Field(ge=0)
    test_end: int = Field(gt=0)


def chronological_split(length: int, *, train_fraction: float = 0.70) -> TimeSplit:
    if length < 2:
        raise ValueError("length must be at least 2")
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    boundary = min(max(int(length * train_fraction), 1), length - 1)
    return TimeSplit(train_start=0, train_end=boundary, test_start=boundary, test_end=length)


def expanding_walk_forward_splits(
    length: int,
    *,
    minimum_train_size: int,
    test_size: int,
    step_size: int | None = None,
) -> list[TimeSplit]:
    """Build expanding-window splits with test data strictly after training."""

    if minimum_train_size < 1 or test_size < 1:
        raise ValueError("minimum_train_size and test_size must be positive")
    step = test_size if step_size is None else step_size
    if step < 1:
        raise ValueError("step_size must be positive")

    splits: list[TimeSplit] = []
    test_start = minimum_train_size
    while test_start + test_size <= length:
        splits.append(
            TimeSplit(
                train_start=0,
                train_end=test_start,
                test_start=test_start,
                test_end=test_start + test_size,
            )
        )
        test_start += step
    return splits
