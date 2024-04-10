import os
from multidefusion.integration import DataIntegration
from multidefusion.results import Figures


def multi_fusion(stations, path, method, noise):
    """Perform data fusion and analysis of the ground deformations for multiple stations.

    Args:
        stations (list or str): List of station names or "ALL" to process all stations found in the specified path.
        path (str): Path to the directory containing station data.
        method (str): Fusion method. Options are "forward" or "forward-backward".
        noise (float): Noise level for data integration [mm/day^2].

    Raises:
        ValueError: If an invalid method is provided.

    Returns:
        None
    """
    port = 8050
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
            fig = Figures(integration)
            if fig.number_of_orbits <= 3:
                fig.create_displacement_plot()
        except ValueError as e:
            print(e)
