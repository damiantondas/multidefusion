import os
import sys
import numpy as np
import pandas as pd
import datetime
from scipy.linalg import block_diag
from typing import Any, Tuple
from multidefusion.datainterface import GNSSData, SARData


class DataIntegration:
    """
    Class for integrating and processing different types of data using the Kalman filter.

    Args:
        station_name (str): The name of the station.
        path (str): The base path where data files are located.
        noise (float): The noise parameter for the Kalman filter.
        port (int): The port is necessary for parallel displaying of subsequent integration results on localhost.

    Attributes:
        station (str): The name of the station.
        path (str): The base path where data files are located.
        data_dict (Dict[str, Dict[str, Any]]): A dictionary containing data objects organized by data type and label. More information about attributes can be found in the API Reference [datainterface module](https://damiantondas.github.io/multidefusion/datainterface/) section.
        mean_data_dict (Dict[str, Dict[str, Any]]): Dictionary to store averaged data after integration is performed.
        predicted_state_and_variance (Dict[datetime.date, Dict[str, Any]]): Predicted state and variance for each date.
        forward (Dict[datetime.date, Dict[str, Any]]): Filtered state and variance for each date.
        backward (Dict[datetime.date, Dict[str, Any]]): Backward estimated state and variance for each date.
        latest_date_all_data (Optional[datetime.date]): The latest date among all data types.
        earliest_date_gnss (Optional[datetime.date]): The earliest date among GNSS data.
        noise (float): The noise parameter for the Kalman filter [mm/day^2 ].
        forward_df_xe (pd.DataFrame): Converted data to pd.DataFrame from forward for xe keys.
        backward_df_xe (pd.DataFrame): Converted data to pd.DataFrame from backward for xe keys.
    """

    N = 6
    TIME_INTERVAL_NUM = 1
    TIME_INTERVAL = 'D'

    def __init__(self, station_name: str, path: str, noise: float, port: int) -> None:
        self.station = station_name
        self.path = os.path.normpath(path)
        self.port = port
        self.data_dict = {}
        self.mean_data_dict = {}
        self.predicted_state_and_variance = {}
        self.forward = {}
        self.backward = {}
        self.latest_date_all_data = None
        self.earliest_date_gnss = None
        self.noise = noise/1000
        self.forward_df_xe = None
        self.backward_df_xe = None

        self.xe = np.zeros((self.N, 1))
        self.system_noise_matrix = self.noise ** 2 * np.kron(np.eye(int(self.N / 2)), np.array(
            [[0.25 * self.TIME_INTERVAL_NUM ** 4, 0.5 * self.TIME_INTERVAL_NUM ** 3],
             [0.5 * self.TIME_INTERVAL_NUM ** 3, self.TIME_INTERVAL_NUM ** 2]]))
        self.transition_matrix = np.kron(np.eye(int(self.N / 2)), np.array([[1, self.TIME_INTERVAL_NUM], [0, 1]]))

    @staticmethod
    def extract_data_type(file_name: str) -> str:
        """
        Extracts data type from the file name.

        Args:
            file_name (str): The name of the data file.

        Returns:
            str: The extracted data type ("GNSS" or "SAR").
        """
        if "GNSS" in file_name:
            return "GNSS"
        elif "DInSAR" in file_name or "PSI" in file_name or "SBAS" in file_name:
            return "SAR"

    @staticmethod
    def create_data_object(data_type: str, file_path: str) -> Any:
        """
        Creates a data object based on the data type.

        Args:
            data_type (str): The type of data ("GNSS" or "SAR").
            file_path (str): The path to the data file.

        Returns:
            Any: An instance of the corresponding data class.
        """
        try:
            if data_type == "GNSS":
                return GNSSData(file_path)
            elif data_type == "SAR":
                return SARData(file_path)
            # Add more conditions for other data types if needed
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
        except ZeroDivisionError:
            sys.exit(1)

    @staticmethod
    def time_update(xe: np.ndarray, Pe: np.ndarray, Phi: np.ndarray, S: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Time update step of the Kalman filter.

        Args:
            xe (np.ndarray): Predicted state.
            Pe (np.ndarray): Variance matrix.
            Phi (np.ndarray): Transition matrix.
            S (np.ndarray): Process noise matrix.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Updated predicted state and variance.
        """
        # number of states
        n = xe.shape[0]

        # check sizes of input
        assert xe.shape[1] == 1, "predicted state must be a column vector"
        assert Pe.shape == (n, n), "variance matrix must be n-by-n"
        assert Phi.shape == (n, n), "transition matrix must be n-by-n"
        assert S.shape == (n, n), "process noise matrix must be n-by-n"

        # time update
        xp = np.dot(Phi, xe)
        Pp = np.dot(np.dot(Phi, Pe), np.transpose(Phi)) + S

        return xp, Pp

    @staticmethod
    def measurement_update(xp: np.ndarray, Pp: np.ndarray, z: np.ndarray, R: np.ndarray, A: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Measurement update step of the Kalman filter.

        Args:
            xp (np.ndarray): Predicted state.
            Pp (np.ndarray): Variance matrix.
            z (np.ndarray): Measurement vector.
            R (np.ndarray): Measurement variance matrix.
            A (np.ndarray): Design matrix.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            Updated estimated state, variance, measurement residual, measurement variance, and Kalman gain.
        """
        # number of states
        n = xp.shape[0]
        # number of measurements
        m = z.shape[0]

        # check sizes of input
        assert xp.shape[1] == 1, "predicted state must be a column vector"
        assert Pp.shape == (n, n), "variance matrix must be n-by-n"
        assert z.shape[1] == 1, "measurements must be a column vector"
        assert R.shape == (m, m), "variance matrix must be m-by-m"
        assert A.shape == (m, n), "design matrix must be m-by-n"

        # measurement update
        v = z - np.dot(A, xp)
        Qv = R + np.dot(np.dot(A, Pp), np.transpose(A))
        K = np.dot(np.dot(Pp, np.transpose(A)), np.linalg.inv(Qv))
        xe = xp + np.dot(K, v)
        Pe = np.dot((np.eye(n) - np.dot(K, A)), Pp)

        return xe, Pe, v, Qv, K

    def remove_bias_in_sar_data(self) -> None:
        """
        Removes bias in SAR data based on GNSS data.

        This method iterates through the SAR data stored in the 'data_dict' attribute and
        applies bias reduction to each dataset, excluding the 'DInSAR' technique. The bias
        reduction is performed using GNSS data up to the earliest date specified by
        'earliest_date_gnss'.

        Note:
        - Bias reduction is applied to each dataset within the SAR data structure.

        Returns:
        None
        """
        if self.data_dict.get("SAR") is not None:
            for technique, data in self.data_dict.get("SAR").items():
                if technique != "DInSAR":
                    if isinstance(data, dict):
                        for orbit, orbit_data in data.items():
                            if isinstance(orbit_data, dict):
                                for _, (subkey, subdata) in enumerate(orbit_data.items()):
                                    subdata.reduce_bias_to_gnss(date=self.earliest_date_gnss)
                            else:
                                orbit_data.reduce_bias_to_gnss(date=self.earliest_date_gnss)

    def connect_data(self) -> None:
        """
        Connects data objects based on data types and labels.
        """
        
        file_list = sorted(os.listdir(os.path.join(self.path, self.station)), key=self.custom_sort)
        try:
            if 'GNSS.txt' not in file_list:
                raise ValueError(f"The GNSS.txt file is missing in the {os.path.join(self.path, self.station)} folder.")
        except ZeroDivisionError:
            sys.exit(1)
            
        data = {}
        orb_elements = {}
        for file_name in file_list:
            file_path = os.path.join(self.path, self.station, file_name)
            data_type = self.extract_data_type(file_name)
            keys = file_name.replace(".txt", '').split("_")
            try:
                if len(keys) > 3:
                    raise ValueError(f"To many separators \'_\' in the {file_name} file name.")
                elif len(keys) == 3 and len(keys[2]) > 10:
                    raise ValueError(f"The sub-name {keys[2]} for is too long and because it exceeds 10 characters.")
            except ZeroDivisionError:
                sys.exit(1)
                            
            if data_type is not None:
                data_obj = self.create_data_object(data_type, file_path)
                current_dict = data
                if len(keys) > 1:
                    orb_elements.setdefault(keys[0], {}).setdefault(keys[1], [])
                    if len(keys) > 2:
                        orb_elements[keys[0]][keys[1]].append(keys[2])
                    else:
                        orb_elements[keys[0]][keys[1]].append('')
                    
                for key in keys[:-1]:
                    if key in ["PSI", "SBAS", "DInSAR"]:
                        current_dict = current_dict.setdefault("SAR", {}).setdefault(key, {})
                    else:
                        current_dict = current_dict.setdefault(key, {})
                current_dict[keys[-1]] = data_obj
                
        uniq_values = {'GNSS': []}
        if keys != ['GNSS']:
            uniq_orbits = set()
            for mainkey, subdict in orb_elements.items():
                uniq_values[mainkey] = []
                for subkey, elements in subdict.items():
                    uniq_values[mainkey].extend(elements)
                    uniq_values[mainkey] = list(set(uniq_values[mainkey]))
                    
                    uniq_orbits.add(subkey)
                        
                    try:
                        if '' in elements:
                            if len(elements) > 1:
                                raise ValueError(f"One of the {mainkey} element for the {subkey} orbit does not have a sub-name determined.")
                            else:
                                uniq_values[mainkey].remove('')
                        elif len(elements) > 9: 
                            raise ValueError(f"The maximum allowed number of elements for the InSAR {subkey} orbit and {mainkey} calculation method is exceeded ({len(elements)} elements). The maximum acceptable number of elements is 9.")
                        
                        if len(uniq_values[mainkey]) > 10: 
                            raise ValueError(f"The maximum allowed number of sub-names for the {mainkey} InSAR calculation method is exceeded (len(uniq_values[mainkey]) sub-names). The maximum acceptable number of sub-names is 10.")
                        elif len(uniq_orbits) > 3:
                             raise ValueError(f"The maximum allowed number of the InSAR orbits is exceeded ({len(uniq_orbits)} orbits). The maximum acceptable number of orbits is 3.")
                    except ZeroDivisionError:
                        sys.exit(1)

        self.number_of_SAR_elements = uniq_values      
        self.data_dict = data
        self.get_latest_date_from_all_data()
        self.get_earliest_gnss_date()
        self.remove_bias_in_sar_data()
        self.sar_data_validation()
        
    def custom_sort(self, item):
        parts = item.replace(".txt", '').split("_")
        prefix = parts[0][0]
        
        suffix  = False
        suffix2 = False
        if len(parts)==1:
            number=False
        else:
            number=parts[1]
        
        if len(parts)<=2:
            suffix = False
        else:
            suffix = parts[2][0].isdigit()
            
            if suffix is True:
                suffix2 = parts[2][0]

        return (prefix, number, suffix, suffix2)

    def sar_data_validation(self):
        """
        Validates SAR data and applies bias reduction if necessary.

        This method iterates through SAR data obtained from different techniques (PSI and SBAS),
        checks if the oldest date in the data is greater than the earliest GNSS date, and applies
        bias reduction if the condition is met.

        Returns:
            None
        """
        for data in self.get_data("SAR", "PSI"):
            if data.oldest_date > self.earliest_date_gnss:
                data.bias_reduction = True
        for data in self.get_data("SAR", "SBAS"):
                 data.bias_reduction = True
        for data in self.get_data("SAR", "DInSAR"):
            if data.oldest_date < self.earliest_date_gnss:
                data.data = data.data[data.data.index >= self.earliest_date_gnss]

    def get_data(self, technique, type):
        """
        Retrieves and flattens data for a specified SAR technique and type.

        Args:
            technique (str): SAR technique (e.g., "SAR").
            type (str): Data type (e.g., "PSI").

        Returns:
            List: Flattened list of data values for the specified technique and type.
        """
        result_list = []
        data = self.data_dict.get(technique, {}).get(type, {})
        for key, values in data.items():
            if isinstance(values, dict):
                for subkey, subvalues in values.items():
                    result_list.append((subvalues))
            else:
                result_list.append((values))
        return result_list

    def kalman_based_bias_removal(self, data_obj, date):
        """
        Applies Kalman-based bias removal to SAR data.

        This method takes a data object and a date, extracts relevant information, performs
        Kalman-based bias removal, and updates the data object with the corrected values.

        Args:
            data_obj (DataObject): Object containing SAR data.
            date (datetime): Date for bias removal.

        Returns:
            None
        """
        start_col = 1 if data_obj.type == "DInSAR" else 0
        rate = 1000 if data_obj.type == "DInSAR" else 1
        head_ang_mean = data_obj.data['HEAD_ANG'].mean()
        inc_ang_mean = data_obj.data['INC_ANG'].mean()
        mat = np.array(
            [np.sin(inc_ang_mean) * np.sin(head_ang_mean), - np.sin(inc_ang_mean) * np.cos(head_ang_mean),
             np.cos(inc_ang_mean)]).reshape(1, -1)
        df = self.forward[date - datetime.timedelta(days=1)]['xe'][start_col::2] * rate
        LOS = np.dot(mat, df).T
        data_obj.data['DSP'] = data_obj.data['DSP'] + LOS[0]
        data_obj.bias_reduction = False

    def get_latest_date_from_all_data(self):
        """
        Updates the latest date among all data types.
        """
        all_dates = []
        if isinstance(self.data_dict, dict):
            for value in self.data_dict.values():
                if isinstance(value, dict):
                    for value2 in value.values():
                        if isinstance(value2, dict):
                            for value3 in value2.values():
                                if isinstance(value3, dict):
                                    for value4 in value3.values():
                                        all_dates.append(value4.latest_date)
                                else:
                                    all_dates.append(value3.latest_date)
                else:
                    all_dates.append(value.latest_date)
        self.latest_date_all_data = max(all_dates, default=None)

    def get_earliest_gnss_date(self):
        """
        Updates the earliest date among GNSS data.
        """
        gnss_dates = self.data_dict.get("GNSS").oldest_date
        self.earliest_date_gnss = gnss_dates

    def _process_data_obj(self, data_obj, date, projection_matrix_list, error_matrix_list, obs_vector_list):
        """Process data from the given data object for a specific date.

           Args:
               data_obj: An object containing data to be processed.
               date: The specific date for which data is to be processed.
               projection_matrix_list: A list to store projection matrices generated during processing.
               error_matrix_list: A list to store error matrices generated during processing.
               obs_vector_list: A list to store observation vectors generated during processing.

           Returns:
               None: This function doesn't return anything; it appends processed data to the provided lists.
        """
        row_data_by_date = data_obj.get_data_by_date(date)
        if row_data_by_date is not None:
            if isinstance(data_obj, SARData) and data_obj.bias_reduction:
                self.kalman_based_bias_removal(data_obj, date)
            projection_matrix, error_matrix = data_obj.create_projection_matrix_and_error(row_data_by_date)
            values = data_obj.get_observation(row_data_by_date)

            projection_matrix_list.append(projection_matrix)
            error_matrix_list.append(error_matrix)
            obs_vector_list.append(values)

    def kalman_forward(self):
        """
        Performs the forward pass of the Kalman filter.
        """
        date_range = pd.date_range(start=self.earliest_date_gnss, end=self.latest_date_all_data, freq=self.TIME_INTERVAL)

        xe = self.xe
        Pe = self.system_noise_matrix
        F = self.transition_matrix
        Q = self.system_noise_matrix

        for date in date_range:
            obs_vector_list = []
            projection_matrix_list = []
            error_matrix_list = []
            for data_type, data_dict in self.data_dict.items():
                if not isinstance(data_dict, dict):
                    self._process_data_obj(data_dict, date, projection_matrix_list, error_matrix_list, obs_vector_list)
                else:
                    for technique, data in data_dict.items():
                        for orbit, orbit_data in data.items():
                            if not isinstance(orbit_data, dict):
                                self._process_data_obj(orbit_data, date, projection_matrix_list, error_matrix_list, obs_vector_list)
                            else:
                                for subkey, subdata in orbit_data.items():
                                    self._process_data_obj(subdata, date, projection_matrix_list, error_matrix_list, obs_vector_list)
            if len(projection_matrix_list) > 0:
                projection_matrix = np.vstack(projection_matrix_list)
                error_matrix = block_diag(*error_matrix_list)
                obs_vector = np.hstack(obs_vector_list).reshape(-1, 1)

            # time update (predict)
            xp, Pp = self.time_update(xe, Pe, F, Q)
            self.predicted_state_and_variance[date] = {"xp": xp, "Pp": Pp}

            # measurement update (estimate)
            xe, Pe, v, Qv, K = self.measurement_update(xp, Pp, obs_vector, error_matrix, projection_matrix)
            self.forward[date] = {"xe": xe, "Pe": Pe}
        self.forward_df_xe = pd.DataFrame(
            [(timestamp, *values["xe"]) for timestamp, values in self.forward.items()],
            columns=["timestamp", "N", "vN", "E", "vE", "U", "vU"]).set_index("timestamp").astype(float)

    def kalman_forward_backward(self):
        """
        Performs the forward-backward pass of the Kalman filter.
        """
        if not self.forward or not self.predicted_state_and_variance:
            self.kalman_forward()
        date_range = pd.date_range(start=self.earliest_date_gnss, end=self.latest_date_all_data, freq=self.TIME_INTERVAL)

        F = self.transition_matrix
        xe_b = self.forward.get(date_range[-1])["xe"]
        Pe_b = self.forward.get(date_range[-1])["Pe"]

        for date in reversed(date_range[:-1]):
            next_day = date + datetime.timedelta(days=self.TIME_INTERVAL_NUM)

            L = np.dot(np.dot(self.forward.get(date)["Pe"], np.transpose(F)), np.linalg.inv(self.predicted_state_and_variance.get(next_day)["Pp"]))
            xe_b = self.forward.get(date)["xe"] + np.dot(L, (xe_b - self.predicted_state_and_variance.get(next_day)["xp"]))
            Pe_b = self.forward.get(date)["Pe"] + np.dot(np.dot(L, (Pe_b - self.predicted_state_and_variance.get(next_day)["Pp"])), np.transpose(L))
            self.backward[date] = {"xe_b": xe_b, "Pe_b": Pe_b}
        self.backward_df_xe = pd.DataFrame(
            [(timestamp, *values["xe_b"]) for timestamp, values in self.backward.items()],
            columns=["timestamp", "N", "vN", "E", "vE", "U", "vU"]).set_index("timestamp").astype(float)

    @staticmethod
    def _process_technique_data(data, container_head, container_inc):
        """
        Process HEAD_ANG and INC_ANG data for a given technique and populates the provided containers.

        Args:
        data (dict): Technique data containing orbit-wise information.
        container_head (dict): Dictionary to store HEAD_ANG data for each orbit.
        container_inc (dict): Dictionary to store INC_ANG data for each orbit.

        Returns:
        None
        """
        for orbit, orbit_data in data.items():
            container_head.setdefault(orbit, [])
            container_inc.setdefault(orbit, [])
            if isinstance(orbit_data, dict):
                for subkey, subdata in orbit_data.items():
                    container_head[orbit].append(subdata.data["HEAD_ANG"])
                    container_inc[orbit].append(subdata.data["INC_ANG"])
            else:
                container_head[orbit].append(orbit_data.data["HEAD_ANG"])
                container_inc[orbit].append(orbit_data.data["INC_ANG"])

    def _process_for_orbit(self, head, inc, cols, name, rate):
        """
        Processes HEAD_ANG and INC_ANG data for a specific orbit, computes the mean Line-of-Sight (LOS),
        and updates the mean_data_dict with forward and backward mean values.

        Args:
        head (dict): Dictionary containing HEAD_ANG data for each orbit.
        inc (dict): Dictionary containing INC_ANG data for each orbit.
        cols (list): List of column names for data extraction.
        name (str): Name to be assigned in the mean_data_dict.
        rate (int): Rate factor to be applied during computation.

        Returns:
        None
        """
        all_orbits = set(self.data_dict.get("SAR", {}).get("PSI", {}).keys()) | set(
            self.data_dict.get("SAR", {}).get("SBAS", {}).keys()) | set(
            self.data_dict.get("SAR", {}).get("DInSAR", {}).keys())

        for orbit in all_orbits:
            head_data = head.get(orbit, None)
            inc_data = inc.get(orbit, None)
            if head_data is not None and inc_data is not None:
                head_ang_mean = pd.concat(head_data, ignore_index=True).mean()
                inc_ang_mean = pd.concat(inc_data, ignore_index=True).mean()

                mat = np.array(
                    [np.sin(inc_ang_mean) * np.sin(head_ang_mean),
                     - np.sin(inc_ang_mean) * np.cos(head_ang_mean),
                     np.cos(inc_ang_mean)
                     ]
                ).reshape(1, -1)

                df = self.forward_df_xe
                df = df[cols] * rate
                LOS = np.dot(mat, df.values.T).T
                LOS = pd.DataFrame(LOS, index=self.forward_df_xe.index)
                self.mean_data_dict.setdefault(name, {}).setdefault(orbit, {})["forward_mean"] = LOS[0]

                if self.backward_df_xe is not None:
                    df = self.backward_df_xe
                    df = df[cols] * rate
                    LOS = np.dot(mat, df.values.T).T
                    LOS = pd.DataFrame(LOS, index=self.backward_df_xe.index)
                    self.mean_data_dict.setdefault(name, {}).setdefault(orbit, {})["backward_mean"] = LOS[0]

    def compute_mean_LOS_orbit(self):
        """
        Computes the mean Line-of-Sight (LOS) orbit for SAR data, including PSI, SBAS, and DInSAR techniques.
        Populates container_head_psi_sbas, container_inc_psi_sbas, container_head_DInSAR, and container_inc_DInSAR
        with HEAD_ANG and INC_ANG data for each orbit.

        Returns:
        None
        """
        container_head_psi_sbas, container_inc_psi_sbas = {}, {}
        container_head_DInSAR, container_inc_DInSAR = {}, {}
        if "SAR" in self.data_dict and self.data_dict.get("SAR") is not None:
            for technique, data in self.data_dict["SAR"].items():
                if technique == "DInSAR":
                    self._process_technique_data(data, container_head_DInSAR, container_inc_DInSAR)
                elif technique == "PSI" or technique == "SBAS":
                    self._process_technique_data(data, container_head_psi_sbas, container_inc_psi_sbas)
            self._process_for_orbit(container_head_psi_sbas, container_inc_psi_sbas, ["N", "E", "U"],
                                    "SAR_SBAS_PSI_MEAN", 1)
            self._process_for_orbit(container_head_DInSAR, container_inc_DInSAR, ["vN", "vE", "vU"], "DInSAR", 1000)
