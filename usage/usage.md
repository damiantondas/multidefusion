# Usage and examples

The software provides integration of permanent **GNSS** data and radar **InSAR** observations, considering a particular computational method such as **DInSAR, SBAS and PSI**.

## Import the library

MultiDEFusion software works in the Python environment (see [Installation](../installation.md)). To run the integration procedure at the beginning import `run_fusion` procedure:
```
from multidefusion import run_fusion
```

## Description of initial parameters

In the following, to `run_fusion`, the initial arguments are required to be defined by the user.

```
integration = run_fusion(stations, path, method, noise)
```

The description of initial parameters:

| Argument   | Type    | Description|
| :---       | :----:  | :---       |
| *stations* | `list` or `str`  | **List** of station names or **"ALL"** to process all stations found in the specified path|
| *path*     | `str`  | Path to the directory containing *station* data|
| *method*   | `str`  | Fusion method. Options are **"forward"** or **"forward-backward"**|
| *noise*    | `float`| Noise level of the integration system [mm/day^2^]

## Important remarks

1. The integration procedure can include a single station folder (e.g., `stations = ["PI01"]`) stored in the `path`, a list of stations (e.g., `stations = ["PI01", "PI02", "PI03"]`) or **ALL** of them (`stations = "ALL"`).

2. For each particular station's folder, it is necessary to store the geodetic data in the ASCII files (see [Input](../input.md)).

3. Every ASCII file stored in the station's folder will be included in the integration procedure with respect to the chosen method (`"forward"` or `"forward-backward"`).

4. The `noise` level expressed as acceleration in mm/day^2^ should by assigned by user in the empirical way.

5. In the library, the zero-mean acceleration model is introduced as the system noise matrix ([Teunissen, 2009](http://hdl.handle.net/20.500.11937/9039)).

## Examples

1. An example script to run fusion for `ALL` stations in `/path/to/multidefusion_trial/` folder using `forward-backward` method with `0.03` mm/day^2^ noise level. To get trial MultiDEFusion repository see [Trail](../trial.md) section:  

    ```
    from multidefusion import run_fusion

    integration = run_fusion(stations="ALL", path="/path/to/multidefusion_trial/", method="forward-backward", noise=0.03)
    ```
2. An example script to run fusion for `PI01` station in `C:\path\to\folder\` folder using `forward` method with `0.05` mm/day^2^ noise level.

    ```
    from multidefusion import run_fusion

    integration = run_fusion(stations=["PI01"], path="C:\path\to\folder\", method="forward", noise=0.05)
    ```

3. An example script to run fusion for `PI01` and `PI05` stations in `C:\path\to\folder\` folder using `forward-backward` method with `0.045` mm/day^2^ noise level.

    ```
    from multidefusion import run_fusion

    integration = run_fusion(stations=["PI01", "PI05"], path="C:\path\to\folder\", method="forward-backward", noise=0.045)
    ```

[Teunissen, P. (2009)](http://hdl.handle.net/20.500.11937/9039). Dynamic data processing: Recursive least-squares.

