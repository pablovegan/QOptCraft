import pytest
import numpy as np

from qoptcraft.state import PureState, State, MixedState, Fock
from qoptcraft.invariant import forbidden_transition, photon_invariant


IN_FOCK = Fock(1, 1, 0, 0)
BELL_STATE = 1 / np.sqrt(2) * Fock(1, 0, 1, 0) + 1 / np.sqrt(2) * Fock(0, 1, 0, 1)

MIXED_STATE = MixedState.from_mixture(pure_states=[IN_FOCK, BELL_STATE], probs=[0.5, 0.5])

HONG_HU_MANDEL_INPUT = PureState([[1, 1]], [1])
HONG_HU_MANDEL_OUTPUT = PureState([[2, 0], [0, 2]], [1 / np.sqrt(2), 1 / np.sqrt(2)])


@pytest.mark.parametrize(
    ("in_state", "out_state", "result"),
    (
        (IN_FOCK, BELL_STATE, True),
        (HONG_HU_MANDEL_INPUT, HONG_HU_MANDEL_OUTPUT, False),
    ),
)
def test_forbidden_transition_reduced(in_state: State, out_state: State, result: bool) -> None:
    test_result = forbidden_transition(in_state, out_state, method="reduced")
    assert result == test_result


@pytest.mark.parametrize(
    ("in_state", "out_state", "result"),
    (
        (IN_FOCK, BELL_STATE, True),
        (HONG_HU_MANDEL_INPUT, HONG_HU_MANDEL_OUTPUT, False),
    ),
)
def test_forbidden_transition_no_basis(in_state: State, out_state: State, result: bool) -> None:
    test_result = forbidden_transition(in_state, out_state, method="no basis")
    assert result == test_result


@pytest.mark.parametrize(
    ("in_state", "out_state", "result"),
    (
        (IN_FOCK, BELL_STATE, True),
        (HONG_HU_MANDEL_INPUT, HONG_HU_MANDEL_OUTPUT, False),
        (IN_FOCK, MIXED_STATE, True),
        (MIXED_STATE, MIXED_STATE, False),
    ),
)
def test_forbidden_transition_basis(in_state: State, out_state: State, result: bool) -> None:
    test_result = forbidden_transition(in_state, out_state, method="basis")
    assert result == test_result


@pytest.mark.parametrize(
    ("state"),
    (BELL_STATE, IN_FOCK, HONG_HU_MANDEL_INPUT, HONG_HU_MANDEL_OUTPUT),
)
def test_equal_photon_invariant(
    state: State,
) -> None:
    invariant_full = photon_invariant(state, method="no basis")
    invariant_basis = photon_invariant(state, method="basis")
    np.isclose(invariant_full, invariant_basis)
