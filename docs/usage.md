# Usage

## Description of software initial parameters

The software provides integration of permanent **GNSS** data and radar **InSAR** observations, considering a particular computational methods such as **DInSAR, SBAS and PSI**.

The integration procedure can include a single station folder (e.g., `stations = ["PI01"]`) stored in the `path`, a list of stations (e.g., `stations = ["PI01", "PI02", ...]`) or ALL of them (`stations = "ALL"`).

For an particular station's folder, it is necessary to store the geodetic data in the ASCII files.
Each file in the station folder will be included in the integration procedure with respect to the chosen method (`"forward"` or `"forward-backward"`).
The `noise` level expressed as acceleration in mm/day^2^ should by assigned by user in the emphiriacal way.

In the library, the zero-mean acceleration model is introduced as the system noise matrix (Teunissen, 2009).

To run the procedure of integration in the Python environment, the initial parameters are required to define by user.

In following, you can find an example script to run fusion for `ALL` stations in `multidefusion_trial` folder using `forward-backward` method with `0.03` mm/day^2^ noise level: 

    ```
    from multidefusion import run_fusion

    integration = run_fusion(stations="ALL", path="/path/to/multidefusion_trial/", method="forward-backward", noise=0.03)
    ```

Teunissen, P. (2009). Dynamic data processing: Recursive least-squares.
