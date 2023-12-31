import numpy as np
import sympy
from numpy.typing import NDArray

from qoptcraft.operators import adjoint_evol
from qoptcraft.basis import get_algebra_basis, BasisAlgebra
from qoptcraft.basis.algebra import sym_matrix, antisym_matrix


class InconsistentEquations(ValueError):
    def __init__(self, rank, expected_rank: float) -> None:
        message = f"The system has rank {rank} but should be {expected_rank}."
        super().__init__(message)


def scattering_from_unitary(unitary: NDArray, modes: int, photons: int) -> NDArray:
    """Retrieve the linear optical scattering matrix from a unitary using Theorem 2
    of PRA 100, 022301 (2019).

    Args:
        unitary (NDArray): unitary matrix.
        modes (int): number of modes in the optical system.
        photons (int): number of photons.

    Returns:
        NDArray: optical scattering matrix that maps to the given unitary.
    """
    coefs = _solution_coefs(unitary, modes, photons)
    basis, _ = get_algebra_basis(modes, photons)

    basis_array = np.array(basis)

    def adjoint(basis_matrix):
        for i in range(len(basis)):
            if (basis_matrix == basis[i]).all():
                index = i
                break
        return np.einsum("k,kij->ij", coefs[index, :], basis_array)

    identity = np.eye(modes)

    def get_nonzero_element():
        for j in range(modes):
            basis_matrix = sym_matrix(j, j, modes)
            for l in range(modes):
                ad_matrix = adjoint(basis_matrix)
                exp_val = np.einsum("i,ij,j->", identity[l, :], ad_matrix, identity[l, :])
                if not np.isclose(exp_val, 0, rtol=1e-5, atol=1e-8):
                    j0, l0 = j, l
                    coef = np.sqrt(-1j * exp_val)
                    return j0, l0, coef
        raise ValueError("Nonzero element not found.")

    j0, l0, coef = get_nonzero_element()
    scattering = np.zeros((modes, modes), dtype=np.complex128)
    for l in range(modes):
        for j in range(modes):
            ad_sym = adjoint(sym_matrix(j, j0, modes))
            sym_term = np.einsum("i,ij,j->", identity[l, :], ad_sym, identity[l0, :])
            if j != j0:
                ad_antisym = adjoint(antisym_matrix(j, j0, modes))
                antisym_term = np.einsum(
                    "i,ij,j->",
                    identity[l, :],
                    ad_antisym,
                    identity[l0, :],
                )
            else:
                antisym_term = 0
            scattering[l, j] = (antisym_term - 1j * sym_term) / coef
    return scattering


def _solution_coefs(unitary: NDArray, modes: int, photons: int) -> NDArray:
    """Coefficients that solve the system of equations that the unitary must satisfy.

    Returns:
        NDArray: matrix with the coefficients that solve the system.
    """
    _, basis_image = get_algebra_basis(modes, photons)
    sol_coefs = []
    for basis_matrix in basis_image:
        eq_matrix = _equation_matrix(modes, basis_image)
        eq_matrix_sym = sympy.Matrix(eq_matrix).T
        reduced_matrix, pivots = eq_matrix_sym.rref()  # reduced row echelon form
        if len(pivots) > modes**2:
            raise InconsistentEquations(len(pivots), modes**2)
        else:
            # If linear independent equations
            indep_term = adjoint_evol(basis_matrix, unitary).ravel()
            solution = np.linalg.solve(eq_matrix[pivots, :], indep_term[pivots, ...])
            sol_coefs.append(solution)
    return np.vstack(sol_coefs, dtype=np.complex128)  # array with sol_coefs elements as rows


def _equation_matrix(modes: int, basis_image: BasisAlgebra) -> NDArray:
    """Matrix of the system of equations.

    Args:
        modes (int): number of modes in the optical system.
        basis_image (BasisAlgebra): basis of the image algebra.

    Returns:
        NDArray: matrix of the system of equations.
    """
    dim = basis_image[0].shape[0]
    eq_matrix = np.empty((dim**2, modes**2), dtype=np.complex128)
    for k in range(dim):
        for l in range(dim):
            for j, basis_matrix in enumerate(basis_image):
                eq_matrix[dim * k + l, j] = basis_matrix[k, l]
    return eq_matrix
