import os
from multidefusion.integration import DataIntegration
from multidefusion.results import Figures


def run_fusion(stations, path, method, noise):
    """The software provides integration of permanent GNSS data and radar InSAR observations, considering a particular computational methods such as DInSAR, SBAS and PSI.
    The integration procedure can include a single 'station' folder (e.g., stations = ["PI01"]) stored in the 'path', a list of stations (e.g., stations = ["PI01", "PI02", ...]) or ALL of them (stations = "ALL").
    For an particular station folder, it is necessary to save the geodetic data as ASCII files.
    Each file in the station folder will be included in the integration procedure with respect to the chosen 'method' ("forward" or "forward-backward").
    The noise level expressed as acceleration in mm/day^2 should by assigned by user in the emphiriacal way.
    In the library, the zero-mean acceleration model is introduced as the system noise matrix (Teunissen, 2009).
    
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
    port = 8050
    integration_results = {}
    if stations == "ALL":
        stations = [f.name for f in os.scandir(path) if f.is_dir()]
    for station in stations:
        print(f"Processing data for station: {station}\n")
        print(f"Kalman {method} integration procedure in progress...")
        integration = DataIntegration(station_name=station, path=path, noise=noise, port=port)
        integration.connect_data()
        port +=1
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
            
    
