"""
BuildWise-AI — Phase 10: Validation and Cross-Validation Helpers

Defines group-aware splitting strategies (GroupKFold and GroupShuffleSplit)
to prevent variant-level and platform-level data leakage across training and test folds.
"""
from typing import Generator, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit


def get_cpu_group_kfold(
    df: pd.DataFrame,
    n_splits: int = 5,
    group_col: str = "group_id",
) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
    """
    Generates GroupKFold cross-validation splits for the CPU dataset.
    
    Guarantees:
    - No platform family group appears in both train and validation sets.
    """
    if group_col not in df.columns:
        raise KeyError(f"Group column '{group_col}' missing from CPU DataFrame")
    
    gkf = GroupKFold(n_splits=n_splits)
    groups = df[group_col].values
    X = np.zeros(len(df))  # Dummy array for split indexing
    
    for train_idx, val_idx in gkf.split(X, groups=groups):
        # Verification of zero group leakage
        train_groups = set(df.iloc[train_idx][group_col])
        val_groups = set(df.iloc[val_idx][group_col])
        assert not train_groups.intersection(val_groups), "Leakage detected: train and validation share groups!"
        yield train_idx, val_idx


def get_gpu_group_kfold(
    df: pd.DataFrame,
    n_splits: int = 4,
    group_col: str = "group_id",
) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
    """
    Generates GroupKFold cross-validation splits for the GPU dataset.
    
    Guarantees:
    - No physical silicon die group appears in both train and validation sets.
    """
    if group_col not in df.columns:
        raise KeyError(f"Group column '{group_col}' missing from GPU DataFrame")
    
    gkf = GroupKFold(n_splits=n_splits)
    groups = df[group_col].values
    X = np.zeros(len(df))
    
    for train_idx, val_idx in gkf.split(X, groups=groups):
        train_groups = set(df.iloc[train_idx][group_col])
        val_groups = set(df.iloc[val_idx][group_col])
        assert not train_groups.intersection(val_groups), "Leakage detected: train and validation share groups!"
        yield train_idx, val_idx


def split_holdout_dataset(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
    group_col: str = "group_id",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits DataFrame into train and holdout test partitions using GroupShuffleSplit.
    """
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    groups = df[group_col].values
    train_idx, test_idx = next(gss.split(df, groups=groups))
    
    train_df = df.iloc[train_idx].reset_index(drop=True)
    test_df = df.iloc[test_idx].reset_index(drop=True)
    
    # Assert zero overlap
    train_groups = set(train_df[group_col])
    test_groups = set(test_df[group_col])
    assert not train_groups.intersection(test_groups), "Leakage detected: train and test share groups!"
    
    return train_df, test_df
