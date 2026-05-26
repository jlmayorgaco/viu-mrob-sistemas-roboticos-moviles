"""Compute the offline discrete LQR gain used by the Bill follower.

The Lua controller embeds the resulting K matrix so CoppeliaSim does not need
SciPy at runtime. State is x = [e_long, e_lat, e_yaw] in the robot frame and
input is u = [delta_v, delta_w] around the reference target behind Bill.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import solve_discrete_are


DT = 0.05
V_REF = 0.22
W_REF = V_REF / 1.55

Q = np.diag([35.0, 80.0, 18.0])
R = np.diag([6.0, 3.0])


def main() -> int:
    a = np.array(
        [
            [0.0, W_REF, 0.0],
            [-W_REF, 0.0, V_REF],
            [0.0, 0.0, 0.0],
        ]
    )
    b = np.array(
        [
            [-1.0, 0.0],
            [0.0, 0.0],
            [0.0, -1.0],
        ]
    )

    ad = np.eye(3) + DT * a
    bd = DT * b
    p = solve_discrete_are(ad, bd, Q, R)
    k = np.linalg.solve(bd.T @ p @ bd + R, bd.T @ p @ ad)
    poles = np.linalg.eigvals(ad - bd @ k)

    print(f"dt = {DT:.6f}")
    print(f"v_ref = {V_REF:.6f}")
    print(f"w_ref = {W_REF:.6f}")
    print("Q =")
    print(Q)
    print("R =")
    print(R)
    print("K =")
    for row in k:
        print("  {" + ", ".join(f"{value:.8f}" for value in row) + "}")
    print("closed_loop_poles = " + ", ".join(f"{pole:.8f}" for pole in poles))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
