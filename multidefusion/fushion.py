import os
from multidefusion.integration import DataIntegration
from multidefusion.results import Figures


def multidefusion(stations, path, method, noise):
    """The software provides integration of permanent GNSS data and radar InSAR observations, considering a particular computational methods such as DInSAR, SBAS and PSI.
    The integration procedure can include a single 'station' folder (e.g., stations = ["PI01"]) stored in the 'path', a list of stations (e.g., stations = ["PI01", "PI02", ...]) or ALL of them (stations = "ALL").
    For an particular station folder, it is necessary to save the geodetic data as ASCII files.
    Each file in the station folder will be included in the integration procedure with respect to the chosen 'method' ("forward" or "forward-backward").
    The noise level expressed as acceleration in mm/day^2 should by assigned by user in the emphiriacal way.
    In the library, the zero-mean acceleration model is introduced as the system noise matrix (Teunissen, 2009).
    
    Teunissen, P. (2009). Dynamic data processing: Recursive least-squares.
    
    The input file names structure:
        1) GNSS: "GNSS.txt" (Mandatory file)
        2) InSAR: e.g., "DInSAR_Asc_1.txt", "DInSAR_Asc_2.txt", "SBAS_51_main.txt", "PSI_123.txt", ...
            - 'Type'_'Orbit'.txt OR
            - 'Type'_'Orbit'_'Element'.txt: The 'Element' part is not mandatory.
    where:
        'Type' is a mandatory signature of InSAR calculation method. Allowed values: "DInSAR", "SBAS" or "PSI".
        'Obrit' is a mandatory signature of InSAR orbit. Allowed values: str or int, e.g., "Asc", "Desc", "51", "123", ...
        'Element' is a non-madatory signature of particular pixel or PS point. Allowed values: str or int, e.g., "1", "10254", "main", ...
    
    Restrictions on the input files:
        1) The "GNSS.txt" is a mandatory file.
        2) The InSAR 'Type' can be realised only by "DInSAR", "SBAS" or "PSI" signature.
        3) The number of distinct InSAR 'Orbit' signatures must be less than or equal to 3.
        4) The number of distinct InSAR 'Element' signatures within particular 'Orbit' must be less than or equal to 9.
        5) The number of distinct InSAR 'Element' signatures within particular 'Type' must be less than or equal to 10.
    
    Headers and data columns structure in the input files:
        1) GNSS : 'YYYY MM DD X Y Z mX mY mZ'
        where:
            YYYY (int)  : Year
            MM   (int)  : Month
            DD   (int)  : Day
            X    (float): Geocentric X coordinate [m]
            Y    (float): Geocentric Y coordinate [m]
            Z    (float): Geocentric Z coordinate [m]
            mX   (float): Error of geocentric X coordinate [m]
            mY   (float): Error of geocentric Y coordinate [m]
            mZ   (float): Error of geocentric Z coordinate [m]
            
        2) DInSAR : 'YYYY1 MM1 DD1 YYYY2 MM2 DD2 DSP INC_ANG HEAD_ANG ERROR'
        where:
            YYYY1    (int)  : Year of primary image
            YYYY2    (int)  : Year of secondary image
            MM1      (int)  : Month of primary image
            MM2      (int)  : Month of secondary image
            DD1      (int)  : Day of primary image
            DD2      (int)  : Day of secondary image
            DSP      (float): LOS displacement [m]
            INC_ANG  (float): Incidence angle [rad]
            HEAD_ANG (float): Heading angle [rad]
            ERROR    (float): Error of LOS displacement [m]
            
        3) SBAS & PSI : 'YYYY MM DDI NC_ANG HEAD_ANG ERROR'
            * The 'ERROR' column can be replaced by: 'COH' (float): Coherence faTeunissen (2009ctor
              Coherence will be converted to the error value expressed in the metric domain using the theory presented in Hansen, 2001 and Tondaś et al., 2023.
              To calculate the error using coherence factor the wavelength of the Sentinel-1 is applied.
              
              Hanssen, R. (2001). Radar interferometry: Data interpretation and error analysis.
              Tondaś, D. et al. (2023). Kalman filter-based integration of GNSS and InSAR observations for local nonlinear strong deformations. 

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
            
    
