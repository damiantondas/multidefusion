import pandas as pd
import numpy as np
import os
import sys
from typing import List, Any, Union, Optional, Tuple
from math import pi, sin, cos, asin, sqrt
from datetime import timedelta


class BaseData:
    """
    Base class for handling common data operations.

    Args:
        path (str): The path to the data file.

    Attributes:
        path (str): The path to the data file.
        sublabel (str): The sublabel extracted from the file path.
        label (str): The label extracted from the file path.
        type (str): The type extracted from the label.
        data (pd.DataFrame): The loaded data.
        latest_date (pd.Timestamp): The latest date in the data.
        oldest_date (pd.Timestamp): The oldest date in the data.
    """

    TIME_INTERVAL_NUM = 1
    TIME_INTERVAL = 'D'

    def __init__(self, path: str) -> None:
        """
        Initializes BaseData object.

        Args:
            path (str): The path to the data file.
        """
        self.path = path
        self.sublabel = None
        self.label = self.add_label_to_data()
        self.type = self.label.split("_")[0]
        self.data = self.load_data()
        self.latest_date = self.data.index.max()
        self.oldest_date = self.data.index.min()

    def load_csv_data(self, header: List[str]) -> pd.DataFrame:
        """
        Loads data from the specified file.

        Args:
            header (List[str]): List of column names.

        Returns:
            pd.DataFrame: Loaded data.
        """
        with open(self.path, 'r') as file:
            first_line = file.readline()
        sep = "\s+|," if "," in first_line else "\s+"
        data = pd.read_csv(self.path, sep=sep, header=None, skiprows=1, names=header, engine="python")
        return data

    def load_data(self) -> pd.DataFrame:
        """
        Abstract method to be implemented by subclasses for loading data.

        Returns:
            pd.DataFrame: Loaded data.
        """
        raise NotImplementedError("Subclasses must implement the load_data method")

    def get_observation(self, row_of_data: Any) -> Any:
        """
        Abstract method to be implemented by subclasses for extracting observations.

        Args:
            row_of_data: A row of data.

        Returns:
            Any: Extracted observation.
        """
        raise NotImplementedError("Subclasses must implement the get_observation method")

    def add_label_to_data(self) -> str:
        """
        Extracts and returns the label and set sublabel from the file path.

        Returns:
            str: Extracted label.
        """
        splitted = os.path.split(self.path)[-1].split(".")[0].split("_")
        if len(splitted) == 3:
            self.sublabel = splitted[-1]
            return splitted[0] + "_" + splitted[1]
        elif len(splitted) == 2:
            return splitted[0] + "_" + splitted[1]
        elif len(splitted) == 1:
            return splitted[0]

    def get_data_by_date(self, date: pd.Timestamp, columns_list: List[str] = None) -> Union[pd.DataFrame, None]:
        """
        Gets data for a specific date.

        Args:
            date (pd.Timestamp): The date for which data is requested.
            columns_list (List[str]): List of column names to be returned.

        Returns:
            Union[pd.DataFrame, None]: Data for the specified date (or None if not found).
        """
        if date in self.data.index:
            data_by_date = self.data.loc[date]
            if not data_by_date.isnull().values.any():
                if columns_list:
                    return data_by_date[columns_list]
                else:
                    return data_by_date
        return None

    def process_timestamp_columns(self) -> None:
        """
        Process timestamp columns in the data.

        Converts GNSS, SBAS, and PSI "YYYY", "MM", "DD" columns into a single "timestamp" column,
        sets it as the index, and resamples the data based on the time interval.
        """
        self.data["timestamp"] = pd.to_datetime(self.data[["YYYY", "MM", "DD"]].astype(int).astype(str).apply(" ".join, 1), format="%Y %m %d")
        self.data = self.data.drop(["YYYY", "MM", "DD"], axis=1)
        self.data.set_index(["timestamp"], inplace=True)
        self.data = self.data.resample(self.TIME_INTERVAL).asfreq()

    def convert_range_into_two_timestamps(self) -> None:
        """
        Convert DInSAR range columns into two timestamp columns.

        Converts "YYYY1", "MM1", "DD1", "YYYY2", "MM2", "DD2" columns into
        "timestamp1" and "timestamp2" columns, and sets them as the index.
        """
        self.data["timestamp1"] = pd.to_datetime(self.data[["YYYY1", "MM1", "DD1"]].astype(int).astype(str).apply(" ".join, 1), format="%Y %m %d")
        self.data["timestamp2"] = pd.to_datetime(self.data[["YYYY2", "MM2", "DD2"]].astype(int).astype(str).apply(" ".join, 1), format="%Y %m %d")
        self.data = self.data.drop(["YYYY1", "MM1", "DD1", "YYYY2", "MM2", "DD2"], axis=1)
        self.data.set_index(["timestamp1", "timestamp2"], inplace=True)

    def replace_decimal_sep(self) -> None:
        """
        Replace decimal separators in non-float columns.

        Replaces commas with dots in non-float columns and converts them to float.
        """
        for column in self.data.columns:
            if self.data[column].dtype != float:
                try:
                    self.data[column] = self.data[column].replace(",", ".", regex=True).astype(float)
                except ValueError:
                    return None

    def create_projection_matrix_and_error(self, row_of_data: pd.Series) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Abstract method to be implemented by subclasses for creating projection matrix and error matrix.

        Args:
            row_of_data (pd.Series): A row of data.

        Returns:
            Tuple[Optional[np.ndarray], Optional[np.ndarray]]: Projection matrix and error matrix.
        """
        raise NotImplementedError("Subclasses must implement the create_projection_matrix_and_error method")


class GNSSData(BaseData):
    """
    Class for handling GNSS data operations, inheriting from BaseData.

    Args:
        path (str): The path to the GNSS data file.

    Attributes:
        Inherits attributes from BaseData.
    """

    HEADER_GNSS = ['YYYY', 'MM', 'DD', 'X', 'Y', 'Z', 'mX', 'mY', 'mZ']

    def __init__(self, path: str) -> None:
        """
        Initializes GNSSData object.

        Args:
            path (str): The path to the GNSS data file.
        """
        super().__init__(path)

    def load_data(self) -> pd.DataFrame:
        """
        Loads GNSS data from the specified file.

        Returns:
            pd.DataFrame: Loaded GNSS data.
        """
        header = getattr(GNSSData, "HEADER_" + self.type)
        self.data = self.load_csv_data(header)

        mean_xyz_first_five_epochs, F = self.create_rotation_matrix()
        self.xyz_to_neu(mean_xyz_first_five_epochs, F)

        self.process_timestamp_columns()
        self.replace_decimal_sep()
        return self.data

    def create_projection_matrix_and_error(self, row_of_data: pd.Series) -> Tuple[Union[np.ndarray, None], Union[np.ndarray, None]]:
        """
        Creates a projection matrix and error matrix based on the provided row of data.

        Args:
            row_of_data (pd.Series): A row of GNSS data.

        Returns:
            Tuple[Union[np.ndarray, None], Union[np.ndarray, None]]: Projection matrix and error matrix.
        """
        if row_of_data is not None:
            projection_matrix = np.array([[1, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0]])
            # error_matrix = np.diag(row_of_data[["mN", "mE", "mU"]].values ** 2) * 100  # ATTENTION!!!! Rephrasing the error due to the results reported by Bernese!!!!
            error_matrix = row_of_data['error']
            return projection_matrix, error_matrix
        return None, None

    def get_observation(self, row_of_data: pd.Series) -> np.ndarray:
        """
        Gets GNSS observation from the provided row of data.

        Args:
            row_of_data (pd.Series): A row of GNSS data.

        Returns:
            np.ndarray: GNSS observation.
        """
        return row_of_data[["N", "E", "U"]].values

    @staticmethod
    def xyz_to_blh(X, Y, Z):
        """
        Converts Cartesian coordinates (X, Y, Z) to geodetic coordinates (latitude, longitude, height).

        Args:
            X (float): Cartesian coordinate in the X direction.
            Y (float): Cartesian coordinate in the Y direction.
            Z (float): Cartesian coordinate in the Z direction.

        Returns:
            Tuple[float, float, float]: Geodetic coordinates (latitude, longitude, height).
        """
        a = 6378137
        b = 6356752.31414
        e2 = ((a * a) - (b * b)) / (a * a)
        elat = 1e-12
        eht = 1e-05
        p = np.sqrt(X ** 2 + Y ** 2)
        lat = np.arctan2(Z, p / (1 - e2))
        h = 0
        dh = 1
        dlat = 1
        i = 0
        while np.any(dlat > elat) or np.any(dh > eht):
            i += 1
            lat0 = lat
            h0 = h
            v = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
            h = p / np.cos(lat) - v
            lat = np.arctan2(Z, p * (1 - e2 * v / (v + h)))
            dlat = np.abs(lat - lat0)
            dh = np.abs(h - h0)
        lon = np.arctan2(Y, X)
        return lat, lon, h

    def create_rotation_matrix(self):
        """
        Creates a rotation matrix based on the mean coordinates of the first five epochs.

        Returns:
            Tuple[pd.Series, np.ndarray]: Mean coordinates of the first five epochs and the rotation matrix.
        """
        mean_xyz_first_five_epochs = self.data.loc[:, ["X", "Y", "Z"]].head(5).mean(axis=0)
        B, L, h = self.xyz_to_blh(mean_xyz_first_five_epochs["X"], mean_xyz_first_five_epochs["Y"], mean_xyz_first_five_epochs["Z"])
        F = np.array([[-np.sin(B) * np.cos(L), -np.sin(B) * np.sin(L), np.cos(B)],
                      [-np.sin(L), np.cos(L), 0],
                      [np.cos(B) * np.cos(L), np.cos(B) * np.sin(L), np.sin(B)]])
        return mean_xyz_first_five_epochs, F

    def xyz_to_neu(self, mean_xyz_first_five_epochs, F):
        """
        Converts Cartesian coordinates (X, Y, Z) to local coordinates (North, East, Up).

        Args:
            mean_xyz_first_five_epochs (pd.Series): Mean coordinates of the first five epochs.
            F (np.ndarray): Rotation matrix.

        Returns:
            None: Modifies the 'data' attribute in-place by updating coordinates and errors.
        """
        columns_to_modify = ["X", "Y", "Z"]

        self.data[columns_to_modify] -= mean_xyz_first_five_epochs[columns_to_modify]

        def calculate_coordinates_and_errors_for_row(row):
            NEU = np.dot(F, np.array([row["X"], row["Y"], row["Z"]]))
            errors = np.dot(np.dot(F, np.diag([row["mX"] ** 2, row["mY"] ** 2, row["mZ"] ** 2])), F.transpose())
            row["N"], row["E"], row["U"] = NEU
            row["error"] = errors
            return row

        self.data = self.data.apply(calculate_coordinates_and_errors_for_row, axis=1)
        self.data = self.data.drop(["X", "Y", "Z", "mX", "mY", "mZ"], axis=1)


class SARData(BaseData):
    """
    Class for handling SAR data operations, inheriting from BaseData.

    Args:
        path (str): The path to the SAR data file.

    Attributes:
        Inherits attributes from BaseData.
    """

    SENTINEL_WAVELENGTH = 0.055465763
    HEADER_DInSAR = ['YYYY1', 'MM1', 'DD1', 'YYYY2', 'MM2', 'DD2', 'DSP', 'INC_ANG', 'HEAD_ANG']
    HEADER_PSI = ['YYYY', 'MM', 'DD', 'DSP', 'INC_ANG', 'HEAD_ANG']
    HEADER_SBAS = ['YYYY', 'MM', 'DD', 'DSP', 'INC_ANG', 'HEAD_ANG']

    def __init__(self, path: str) -> None:
        """
        Initializes SARData object.

        Args:
            path (str): The path to the SAR data file.
        """
        super().__init__(path)
        self.bias_reduction = False
        self.get_header_from_file()

    def get_header_from_file(self):
        with open(self.path, 'r') as file:
            first_line = file.readline()
        try:
            if 'COH' in first_line:
                header = getattr(SARData, "HEADER_" + self.type) + ["COH"]
                return header
            elif 'ERROR' in first_line:
                header = getattr(SARData, "HEADER_" + self.type) + ["ERROR"]
                return header
            else:
                raise ValueError(f"The header cannot be identified in the {self.path} file.")
        except ZeroDivisionError:
            sys.exit(1)

    def load_data(self) -> pd.DataFrame:
        """
        Loads SAR data from the specified file.

        Returns:
            pd.DataFrame: Loaded SAR data.
        """
        header = self.get_header_from_file()
        self.data = self.load_csv_data(header)
        self.replace_decimal_sep()
        if "COH" in header:
            self.coherence_to_error()
        if self.type == "DInSAR":
            self.convert_range_into_two_timestamps()
        else:
            self.process_timestamp_columns()
        self.expand_dataframe_by_date_range()
        return self.data

    def reduce_bias_to_gnss(self, date: pd.Timestamp):
        """
        Reduces bias in SAR data to GNSS data.

        This method reduces the bias in the SAR data by removing data points prior to
        the specified date and adjusting the 'DSP' values based on the first non-null value
        after the specified date.

        Args:
            date (pd.Timestamp): The timestamp used as a reference point for bias reduction.

        Returns:
            None
        """
        self.data = self.data[self.data.index > date]
        first_non_null_value = self.data["DSP"].first_valid_index()
        if first_non_null_value is not None:
            self.data["DSP"] = self.data["DSP"] - self.data.at[first_non_null_value, "DSP"]

    def coherence_to_error(self) -> None:
        """
        Convert coherence column to error column in the data.
        """
        sentinel_wavelength = self.SENTINEL_WAVELENGTH

        def calculate_error(coherence: float) -> float:
            """
            Calculate error from coherence.

            Args:
                coherence (float): Coherence value.

            Returns:
                float: Calculated error.
            """
            li = 0
            k = 1
            while True:
                li += (coherence ** (2 * k)) / (k ** 2)
                li2 = li + (coherence ** (2 * k)) / (k ** 2)
                if abs(li - li2) <= 1e-10:
                    break
                k += 1
            phase = pi ** 2/3 - pi * asin(coherence) + asin(coherence) ** 2 - 0.5 * li2
            return sqrt(phase) * sentinel_wavelength / (4 * pi)

        self.data["ERROR"] = self.data["COH"].apply(calculate_error)

    def create_projection_matrix_and_error(self, row_of_data: pd.Series) -> Tuple[Optional[np.ndarray], Optional[float]]:
        """
        Creates a projection matrix and error from the provided row of data.

        Args:
            row_of_data (pd.Series): A row of SAR data.

        Returns:
            Tuple[Optional[np.ndarray], Optional[float]]: Projection matrix and error.
        """
        if row_of_data is not None:
            inc_ang = row_of_data["INC_ANG"]
            head_ang = row_of_data["HEAD_ANG"]
            error = row_of_data["ERROR"]
            if self.type == "DInSAR":
                projection_matrix = np.array([[0, sin(inc_ang) * sin(head_ang), 0, -sin(inc_ang) * cos(head_ang), 0, cos(inc_ang)]])
            else:
                projection_matrix = np.array([[sin(inc_ang) * sin(head_ang), 0, -sin(inc_ang) * cos(head_ang), 0, cos(inc_ang), 0]])
            error_matrix = error ** 2
            return projection_matrix, error_matrix
        return None, None

    def get_observation(self, row_of_data: pd.Series) -> Union[float, None]:
        """
        Gets SAR observation from the provided row of data.

        Args:
            row_of_data (pd.Series): A row of SAR data.

        Returns:
            Union[float, None]: SAR observation.
        """
        return row_of_data["DSP"]

    def expand_dataframe_by_date_range(self) -> None:
        """
        Expands the DataFrame by date range for "DInSAR" label.

        For SAR data labeled as "DInSAR", this method adds a temporary column "temp" to the DataFrame
        containing a date range between "timestamp1" and "timestamp2" based on the specified time interval.
        The DataFrame is then exploded based on the "temp" column, duplicates are removed, and unnecessary
        columns are dropped to create a new "timestamp1" index.

        Note:
        - This method is specifically designed for SAR data labeled as "DInSAR".
        - It modifies the existing DataFrame in-place.

        Example:
        If the original DataFrame has a row with "timestamp1" and "timestamp2" as ["2022-01-01", "2022-01-03"],
        and the time interval is set to "1D" (daily), the resulting DataFrame will have individual rows for
        "2022-01-01", "2022-01-02", and "2022-01-03".
        """
        if self.type == "DInSAR":
            # Create a new column to store timestamps from the range of the given row
            self.data["temp"] = self.data.apply(
                lambda row: pd.date_range(
                    row.name[0],
                    row.name[1] - timedelta(days=self.TIME_INTERVAL_NUM),
                    freq=self.TIME_INTERVAL
                ),
                axis=1
            )
            # Count the difference in days for each row between the date range
            self.data["day_diff"] = (self.data.index.get_level_values(1) - self.data.index.get_level_values(0)).days
            # Calculate rates of daily changes
            self.data["DSP"] = self.data["DSP"] / self.data["day_diff"]
            # Extend DataFrame to a specific time interval and add NaN where data is missing
            self.data = (
                self.data.explode("temp")
                .reset_index()
                .drop_duplicates(subset="temp", keep="last")
                .drop(columns=["timestamp1", "timestamp2", "day_diff"])
                .rename(columns={"temp": "timestamp1"})
                .set_index("timestamp1")
                .resample(self.TIME_INTERVAL)
                .asfreq()
            )
