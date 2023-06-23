"""Copyright 2021 Daniel Gómez Aguado

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

import warnings

import numpy as np
from scipy.optimize import fsolve

from .optical_elements import beam_splitter_reck

# The functions evenFunction(z) and oddFunction(z) find the required values of theta and phi
# for each decomposition, by using two conditions: the real and imaginary values


def decomposition_reck(M, dim, output, name, txt=False):
    # We declare those variables as global in orden to use them in odd/evenFunction(z)
    global m
    global n
    global j
    global i

    # Easier to comprehend dimension and matrix declarations
    global N
    N = dim
    global M_current
    M_current = np.array(M)

    # Steps counter
    cont = 0

    TmnList = np.zeros((int(N * (N - 1) / 2), N, N), dtype=complex)

    for i in range(N, 1, -1):
        m = i
        for j in range(1, i):
            n = i - j
            zGuess = np.ones(2)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sol = fsolve(oddFunction, zGuess)
            # The computation changes compared to the even case
            M_current = M_current.dot(beam_splitter_reck(sol[0], sol[1], N, m - 1, n - 1))
            TmnList[cont, :, :] = beam_splitter_reck(sol[0], sol[1], N, m - 1, n - 1)

            cont += 1

    return TmnList, M_current


def oddFunction(z):
    global M_current
    global N
    global m
    global n

    theta = z[0]
    phi = z[1]

    T = beam_splitter_reck(theta, phi, N, m - 1, n - 1)

    # This time, we apply the dot product in the other side of the matrix
    f0 = np.real(M_current[m - 1, :].dot(T[:, n - 1]))
    f1 = np.imag(M_current[m - 1, :].dot(T[:, n - 1]))

    return np.array([f0, f1])


def phase_adjust(phase, minn=-np.pi, maxx=np.pi):
    while phase < minn:
        phase += 2.0 * np.pi

    while phase > maxx:
        phase -= 2.0 * np.pi

    return phase
