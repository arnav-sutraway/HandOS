import numpy as np


class CursorKalman2D:
    """
    Constant-velocity Kalman filter on screen space.
    State: [x, y, vx, vy]^T. Observations: [x, y].
    """

    def __init__(
        self,
        dt: float,
        process_noise: float = 2.0,
        measurement_noise: float = 25.0,
    ) -> None:
        self.dt = max(dt, 1e-4)
        self.F = np.array(
            [
                [1.0, 0.0, dt, 0.0],
                [0.0, 1.0, 0.0, dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        self.H = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]], dtype=np.float64)
        self.Q = np.eye(4, dtype=np.float64) * process_noise
        self.R = np.eye(2, dtype=np.float64) * measurement_noise
        self.I = np.eye(4, dtype=np.float64)
        self.x = np.zeros((4, 1), dtype=np.float64)
        self.P = np.eye(4, dtype=np.float64) * 500.0
        self._initialized = False

    def set_dt(self, dt: float) -> None:
        self.dt = max(float(dt), 1e-4)
        self.F = np.array(
            [
                [1.0, 0.0, self.dt, 0.0],
                [0.0, 1.0, 0.0, self.dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

    def reset(self) -> None:
        self.x[:] = 0.0
        self.P = np.eye(4, dtype=np.float64) * 500.0
        self._initialized = False

    def init_from_measurement(self, mx: float, my: float) -> None:
        self.x[0, 0] = mx
        self.x[1, 0] = my
        self.x[2, 0] = 0.0
        self.x[3, 0] = 0.0
        self.P = np.eye(4, dtype=np.float64) * 200.0
        self._initialized = True

    def step(self, mx: float, my: float) -> tuple[float, float]:
        if not self._initialized:
            self.init_from_measurement(mx, my)
            return float(self.x[0, 0]), float(self.x[1, 0])

        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

        z = np.array([[mx], [my]], dtype=np.float64)
        y_res = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y_res
        self.P = (self.I - K @ self.H) @ self.P

        return float(self.x[0, 0]), float(self.x[1, 0])
