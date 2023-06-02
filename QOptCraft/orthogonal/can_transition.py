"""Module docstrings.
"""
import numpy as np
from scipy.special import factorial as fact

from QOptCraft.state import State, PureState
from .mat_inner_product import mat_inner_product
from .gram_schmidt import gram_schmidt
from QOptCraft.basis import get_algebra_basis


def can_transition(input_: State, output: State) -> bool:
    """Check if we cannot transition from an input state to an output state
    through an optical network. It is just a necessary condition, so if the
    output is True, we cannot know if there is a transition matrix.
    """
    assert input_.photons == output.photons, "Number of photons don't coincide."
    assert input_.modes == output.modes, "Number of modes don't coincide."

    basis_img_algebra = get_algebra_basis(input_.modes, input_.photons)[1]
    orthonormal_basis = gram_schmidt(basis_img_algebra)

    in_coefs = []
    out_coefs = []
    for basis_matrix in orthonormal_basis:
        in_coefs.append(mat_inner_product(1j * input_.density_matrix, basis_matrix))
        out_coefs.append(mat_inner_product(1j * output.density_matrix, basis_matrix))

    in_energy = sum(np.abs(in_coefs) ** 2)
    out_energy = sum(np.abs(out_coefs) ** 2)
    in_energy = round(in_energy, 7)
    out_energy = round(out_energy, 7)

    print(f"In energy = {in_energy} \t\t Out energy = {out_energy}")

    return np.isclose(in_energy, out_energy)


def photon_invariant(input_: PureState, output: PureState):
    """Check if we cannot transition from an input state to an output state
    through an optical network. The function tests if the invariant defined in
    corollary 3 is conserved.
    """
    assert input_.photons == output.photons, "Number of photons don't coincide."
    assert input_.modes == output.modes, "Number of modes don't coincide."

    modes = input_.modes
    in_invariant = 0
    out_invariant = 0

    for mode_1 in range(modes):
        for mode_2 in range(mode_1 + 1, modes):
            in_invariant += input_.exp_photons(mode_1, mode_2) * input_.exp_photons(mode_2, mode_1)
            in_invariant -= input_.exp_photons(mode_1, mode_1) * input_.exp_photons(mode_2, mode_2)

            out_invariant += output.exp_photons(mode_1, mode_2) * output.exp_photons(mode_2, mode_1)
            out_invariant -= output.exp_photons(mode_1, mode_1) * output.exp_photons(mode_2, mode_2)

    in_invariant = round(in_invariant, 7)
    out_invariant = round(out_invariant, 7)

    return in_invariant, out_invariant


def can_transition_no_basis(input_: PureState, output: PureState) -> bool:
    """Check if we cannot transition from an input state to an output state
    through an optical network. The function tests if the invariant defined in
    corollary 3 is conserved.
    """
    in_invariant, out_invariant = photon_invariant(input_, output)

    modes = input_.modes
    photons = input_.photons

    photons = input_.photons
    C1 = (modes * photons + 1) * fact(modes) * fact(photons) / fact(modes + photons)
    C2 = 2 * fact(modes + 1) * fact(photons - 1) / fact(modes + photons)
    if np.isnan(C1):
        C1 = 0
    if np.isnan(C2):
        C2 = 0
    # print(f"In invariant = {in_invariant} \t\t Out invariant = {out_invariant}")
    print(f"\nIn invariant = {C1 + C2 * in_invariant} \t Out invariant = {C1 + C2 * out_invariant}")

    return np.isclose(in_invariant, out_invariant)
