import os
from multidefusion.integration import DataIntegration
from multidefusion.results import Figures


def run_fusion(stations, path, method, noise):
    """
    The library is based on geodetic observations stored in the form of text files. Maintenance of the specific structure for all input files is necessary to ensure the successful completion of the integration procedure. 
    
    Important remarks:
    1. The integration procedure can include a single station folder (e.g., stations = ["PI01"]) stored in the path, a list of stations (e.g., stations = ["PI01", "PI02", "PI03"]) or ALL of them (stations = "ALL").
    2. For each particular station's folder, it is necessary to store the geodetic data in the ASCII files (see [Input](../input.md)).
    3. Every ASCII file stored in the station's folder will be included in the integration procedure with respect to the chosen method ("forward" or "forward-backward").
    4. The noise level expressed as acceleration in mm/day^2^ should by assigned by user in the empirical way.
    5. In the library, the zero-mean acceleration model is introduced as the system noise matrix (Teunissen, 2009).
    
    Teunissen, P. (2009). Dynamic data processing: Recursive least-squares.
    
    Args:
        stations (list or str): List of station names or "ALL" to process all stations found in the specified path.
        path (str): Path to the directory containing station data.
        method (str): Fusion method. Options are "forward" or "forward-backward".
        noise (float): Noise level of the integration system [mm/day^2].

    Raises:
        ValueError: If an invalid method is provided.

    Returns:
        integration_results (dict): DataIntegration objects
    """
    port = 8049
    integration_results = {}
    if stations == "ALL":
        stations = [f.name for f in os.scandir(path) if f.is_dir()]
    for station in stations:
        print(f"\nFusion started for station: {station}\n")
        print(f"Kalman {method} integration procedure in progress.")
        port +=1
        integration = DataIntegration(station_name=station, path=path, noise=noise, port=port)
        integration.connect_data()
        try:
            if method == "forward":
                integration.kalman_forward()
            elif method == "forward-backward":
                integration.kalman_forward_backward() 
            else:
                raise ValueError(f"Invalid method '{method}'. Please enter 'forward' or 'forward-backward'.")
            integration.compute_mean_LOS_orbit()
            integration_results[station] = integration
            
            fig = Figures(integration)
            fig.create_displacement_plot()
            
        except ValueError as e:
            print(e)
            
    return integration_results
            
    
