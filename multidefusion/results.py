import plotly.graph_objects as go
import plotly.subplots as sp
from dateutil.relativedelta import relativedelta
import pandas as pd
from statistics import mean
from dash import dash, dcc, html, Input, Output, ctx
import webbrowser

class Figures:
    """Class for creating displacement plots.
    
    The final plot is created involving the Plotly library and Dash framework. The graphic representation of the results is automatically launched on the localhost server on port 8050.

    The most important plot features:

    1. Visualisation: The default port for displaying results on localhost is 8050. For more than one station, the outputs will be displayed simultaneously on consecutive ports.
    2. Legend: Work for all of the traces and provide a general overview of the results by activating or deactivating groups of data using the legend entities.
    3. Hover: Working within a single trace and providing a detailed overview of the results using the cursor.
    4. Table: To provide the most relevant information about the integration procedure.
    5. Customisation: To provide individual ranges for dates or values:
        - Dates range: adjustable by providing initial and last date or by using the calendar.
        - Horizontal range: adjustable by providing minimum and maximum values.
        - Vertical & LOS range: adjustable by providing minimum and maximum values.
        - Rate range: adjustable by providing minimum and maximum values.
    6. Buttons: To facilitate manipulation between the traces:
        - Restore default: Restore the original ranges of dates or values after user manipulations.
        - Sync ranges: To synchronise the ranges to the same values (by default, the horizontal and vertical ranges of displacement are disjoint).
    7. Mode bar: A default toolbar of the plotly library located in the top right corner:
        - Download plot: To save the plot in svg format after user's manipulations.
        - Edit in Chart Studio: To provide more advanced modifications in the plotly Chart Studio.
        - Zoom: Work for a selected part of the trace. Double click on the trace to zoom back out.
        - Pan: Working within a single trace by moving the current view of the trace.
        - Draw line: Working within a single trace.
        - Draw circle: Working within a single trace.
        - Draw rectangle: Working within a single trace.
        - Erase the active shape: A single-click to activate the shape.
        - Zoom in: Work simultaneously for all of the traces.
        - Zoom out: Work simultaneously for all of the traces.
        - Reset axes: Work simultaneously for all of the traces.
    """
    def __init__(self, data_integration):
        """
        Initialize Figures object.

        Args:
            data_integration (object): Object containing integrated data.
        """
        self.data_integration = data_integration
        sar_data = self.data_integration.data_dict.get("SAR")
        if sar_data is not None:
            list_of_orbits = list(set(orbit for technique_data in sar_data.values() for orbit in technique_data))
            list_of_orbits = [int(x) for x in list_of_orbits]
            list_of_orbits.sort()
            list_of_orbits = [str(x) for x in list_of_orbits]
            self.orbits = list_of_orbits
            self.number_of_orbits = len(self.orbits)
            self.sar_data_types = list(set([data for data in self.data_integration.data_dict.get("SAR").keys()]))
        else:
            self.orbits = []
            self.number_of_orbits = 0
            self.sar_data_types = []

    @staticmethod
    def find_min_value(*lists):
        """
        Find the minimum value from a set of lists.

        Args:
            *lists: Variable number of lists to find the minimum value from.

        Returns:
            Minimum value from the provided lists.
        """
        if not lists:
            return None
        flattened_list = [item for sublist in lists for item in sublist]
        return min(flattened_list)

    @staticmethod
    def find_max_value(*lists):
        """
        Find the maximum value from a set of lists.

        Args:
            *lists: Variable number of lists to find the maximum value from.

        Returns:
            Maximum value from the provided lists.
        """
        if not lists:
            return None
        flattened_list = [item for sublist in lists for item in sublist]
        return max(flattened_list)
    
    @staticmethod
    def find_max_total(df):
        """
        Find the maximum value (positive or negative) from each column from a set of dataframe.

        Args:
            df: dataframe

        Returns:
            Maximum value from from each column from a set of dataframe.
        """
        return df.apply(lambda col: col.max() if col.max() >= -col.min() else col.min(), axis=0)
    
    @staticmethod
    def add_vline(fig, timestamp_min_value, timestamp_max_value, row, col):    
        """
        Add Thicker line for each subplot to indicate the beginning of a year

        Args:
            fig: Figure
            timestamp_min_value: Earliest date
            timestamp_max_value: Lastest date
            row: figure's row
            col: figure's column

        Returns:
            None
        """
        [fig.add_shape(x0=date, x1=date, y0=-10, y1=10, type="line", line=dict(color='lightgray', width=2), layer="below", row=row, col=col) for date in
        pd.date_range(start=timestamp_min_value - relativedelta(years=2),
        end=timestamp_max_value + relativedelta(years=2), freq='YS')]

    def create_displacement_plot(self):
        """
        Create displacement plot using Plotly and Dash.
        """
        # SETTINGS
        print("Development of a figure...")
        additional_range = 0.05  # additional +/-5% of range for plots by x and y axis
        golden_ratio = (1 + 5 ** 0.5) / 2  # for size on y axis
        subplots_postition = {'3*': [[0.019, 0.335], [0.342, 0.658], [0.665, 0.981]],
                              '3' : [[0.000, 0.316], [0.323, 0.639], [0.684, 1.000]],
                              '2' : [[0.1805, 0.4965], [0.5035, 0.8195]],
                              '1' : [[0.323, 0.639]]}
        
        shift_rate_fig  = 0.007
        shift_disp_fig  = 0.100
        shift_title_fig = 0.003
        shift_legend    = 0.030
        rate_fig_size   = 7/25
        top_limit_plot  = 0.970
        vertical_postition = {}
        vertical_postition['1']  = [top_limit_plot-subplots_postition['3'][0][1]/golden_ratio, top_limit_plot]
        vertical_postition['2']  = [vertical_postition['1'][0]-subplots_postition['3'][0][1]/golden_ratio*rate_fig_size-shift_rate_fig , vertical_postition['1'][0]-shift_rate_fig]
        vertical_postition['3*'] = [vertical_postition['2'][0]-subplots_postition['3'][0][1]/golden_ratio*rate_fig_size-shift_disp_fig , vertical_postition['2'][0]-shift_disp_fig]
        vertical_postition['3']  = [vertical_postition['2'][0]-subplots_postition['3'][0][1]/golden_ratio              -shift_disp_fig , vertical_postition['2'][0]-shift_disp_fig]
        vertical_postition['4']  = [vertical_postition['3'][0]-subplots_postition['3'][0][1]/golden_ratio*rate_fig_size-shift_rate_fig , vertical_postition['3'][0]-shift_rate_fig]
        
        table_postition = {'GNSS'  : [vertical_postition['2'][0]-subplots_postition['3'][0][1]/golden_ratio-shift_disp_fig, vertical_postition['2'][0]-shift_disp_fig],
                           'DInSAR': [vertical_postition['3*'][0]-subplots_postition['3'][0][1]/golden_ratio-shift_disp_fig, vertical_postition['3*'][0]-shift_disp_fig],
                           'SBAS'  : [vertical_postition['3'][0]-subplots_postition['3'][0][1]/golden_ratio-shift_disp_fig, vertical_postition['3'][0]-shift_disp_fig],
                           'MSAR'  : [vertical_postition['4'][0]-subplots_postition['3'][0][1]/golden_ratio-shift_disp_fig, vertical_postition['4'][0]-shift_disp_fig]}
        
        shift_dash = 0
        max_len_elements = max(len(lst) for lst in self.data_integration.number_of_SAR_elements.values())
        if max_len_elements > 2:
            shift_dash = (max_len_elements-2)*7
            
        custom_position = {'GNSS'  : 558,
                           'DInSAR': 754+shift_dash,
                           'SBAS'  : 929+shift_dash,
                           'MSAR'  : 1009+shift_dash}
        
        rows = 3
        cols = 3
        specs = [[{"type": "xy"}] * cols for _ in range(rows-1)]
        
        # COLORS BY DATA TYPE
        data_colors = {"forward": "rgb(25, 255, 25)",
                       "backward": "rgb(255, 0, 0)",
                       "GNSS": "rgb(0, 190, 255)",

                       "DInSAR":["#0000ff", '#1322FB', '#2541F8', '#375DF6', '#4976F3', '#5A8CF2', '#6AA0F0', '#7BB1EF', '#8AC0EF', '#9ACDEF'],
                       "PSI":   ["#771e87", '#782390', '#792999', '#7A2FA2', '#7A36AB', '#7A3DB3', '#7A45BA', '#7B54BB', '#7E62BC', '#8370BD'],
                       "SBAS":  ["#7f822f", '#8C8936', '#938B3E', '#9B8D46', '#A28E4E', '#A89057', '#AA9064', '#AC9372', '#AE967E', '#B19C8B'],
                       }

        disp_cols  = ["N", "E", "U"]
        rate_cols  = ["vN", "vE", "vU"]
        disp_units = {"U": "ver", "N": "hor", "E": "hor"}

        # CREATE STORAGE FOR STORE MIN AND MAX FOR SPECIFIC DATA TYPE VALUES
        max_disp = {"ver": [], "hor": []}
        min_disp = {"ver": [], "hor": []}
        max_rate = []
        min_rate = []
        
        name_forward = "Forward"
        name_backward = "Backward"

        subplot_titles = ["<b>North</b>", "<b>East</b>", "<b>Up</b>"] + [''] * cols

        orbit_titles = ["<b>Orbit " + orbit + "</b>" for orbit in self.orbits]
        empty_titles = [""] * (3 - self.number_of_orbits)
        
        # CREATE GRID FOR SUBPLOTS AND TITLES
        if "PSI" in self.sar_data_types or "SBAS" in self.sar_data_types:
            rows += 1
            subplot_titles.extend(orbit_titles + empty_titles)

            specs_temp = [[{"type": "xy"}] * self.number_of_orbits + [None] * (3 - self.number_of_orbits)]
            specs.extend(specs_temp)

        if "DInSAR" in self.sar_data_types:
            rows += 1
            specs_temp = [[{"type": "xy"}] * self.number_of_orbits + [None] * (3 - self.number_of_orbits)]
            specs.extend(specs_temp)
            if "PSI" not in self.sar_data_types and "SBAS" not in self.sar_data_types:
                subplot_titles.extend(orbit_titles + empty_titles)
            else:
                subplot_titles.extend([""] * self.number_of_orbits)
                
        specs_temp = [ [{"type": "table"}] + [None]*2]
        specs.extend(specs_temp)
        
        # CREATE FIG OBJECT
        fig = sp.make_subplots(rows=rows, cols=cols,
                               specs=specs,
                               subplot_titles=subplot_titles, shared_xaxes=True, )

        # GET TIMESTAMPS FOR GNSS, FORWARD, BACKWARD IF EXIST
        gnss_timestamp = self.data_integration.data_dict['GNSS'].data.index
        forward_timestamp = self.data_integration.forward_df_xe.index
        backward_timestamp = self.data_integration.backward_df_xe.index if self.data_integration.backward_df_xe is not None else None
        timestamp_min_value = self.find_min_value(gnss_timestamp, forward_timestamp,
                                                  backward_timestamp) if backward_timestamp is not None else self.find_min_value(
            gnss_timestamp, forward_timestamp)
        timestamp_max_value = self.find_max_value(gnss_timestamp, forward_timestamp,
                                                  backward_timestamp) if backward_timestamp is not None else self.find_max_value(
            gnss_timestamp, forward_timestamp)

        # CREATE DATES RANGE INCLUDING ADDITIONAL RANGE
        additional_range_abs = additional_range * abs(timestamp_max_value - timestamp_min_value)
        dates_range = [timestamp_min_value - additional_range_abs, timestamp_max_value + additional_range_abs]
        
        # ITERATION FOR GNSS DATA
        for i, coord in enumerate(disp_cols):
            showlegend = True if i == 0 else False
            disp_gnss = self.data_integration.data_dict['GNSS'].data[coord]
            disp_forward = self.data_integration.forward_df_xe[disp_cols[i]]
            rate_forward = self.data_integration.forward_df_xe[rate_cols[i]] * 1000
            disp_type = disp_units.get(coord, None)
            if disp_type:
                max_disp[disp_type].extend([max(disp_gnss), max(disp_forward)])
                min_disp[disp_type].extend([min(disp_gnss), min(disp_forward)])
            max_rate.extend([max(rate_forward)])
            min_rate.extend([min(rate_forward)])

            fig.add_trace(
                go.Scatter(x=gnss_timestamp, y=disp_gnss, mode='markers', name='', showlegend=showlegend,
                           legendgroup="GNSS", legendgrouptitle_text="GNSS", marker=dict(color=data_colors["GNSS"], size = 8)), 
                row=1, col=i + 1)
            fig.add_trace(
                go.Scatter(x=forward_timestamp, y=disp_forward, mode='lines', name=name_forward, showlegend=showlegend,
                           legendgroup="kalman", legendgrouptitle_text="Kalman",
                           line=dict(width=5, color=data_colors["forward"])), row=1, col=i + 1)
            fig.add_trace(
                go.Scatter(x=forward_timestamp, y=rate_forward, mode='lines', name=name_forward, showlegend=False,
                           legendgroup="kalman", legendgrouptitle_text="Kalman",
                           line=dict(width=5, color=data_colors["forward"])), row=2, col=i + 1)
            
            self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=1, col=i + 1)
            self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=2, col=i + 1)

            if self.data_integration.backward_df_xe is not None:
                disp_backward = self.data_integration.backward_df_xe[disp_cols[i]]
                rate_backward = self.data_integration.backward_df_xe[rate_cols[i]] * 1000

                if disp_type:
                    max_disp[disp_type].extend([max(disp_backward)])
                    min_disp[disp_type].extend([min(disp_backward)])
                max_rate.extend([max(rate_backward)])
                min_rate.extend([min(rate_backward)])

                fig.add_trace(go.Scatter(x=backward_timestamp, y=disp_backward, mode='lines', name=name_backward,
                                         showlegend=showlegend, legendgroup="kalman",
                                         line=dict(width=4, color=data_colors["backward"])), row=1, col=i + 1)
                fig.add_trace(go.Scatter(x=backward_timestamp, y=rate_backward, mode='lines', name=name_backward,
                                         showlegend=False, legendgroup="kalman",
                                         line=dict(width=4, color=data_colors["backward"])), row=2, col=i + 1)

        # ITERATION FOR SAR DATA - only DSP
        if self.data_integration.data_dict.get('SAR') is not None:
            for technique, data in self.data_integration.data_dict.get('SAR').items():
                row = 3
                if technique == "DInSAR" and ("SBAS" in self.sar_data_types or "PSI" in self.sar_data_types):
                    row = 4
                if technique == "DInSAR":
                    for orbit in set(self.orbits).difference(set(data.keys())):
                        col = self.orbits.index(orbit) + 1 if self.number_of_orbits > 1 else 1
                        fig.add_trace(
                            go.Scatter(x=dates_range, y=pd.Series(dtype=object), mode='markers',
                                       showlegend=False), row=row, col=col)
                        self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=row, col=col)
                else:
                    for orbit in set(self.orbits).difference(set(data.keys())):
                        col = self.orbits.index(orbit) + 1 if self.number_of_orbits > 1 else 1
                        fig.add_trace(
                            go.Scatter(x=dates_range, y=pd.Series(dtype=object), mode='markers',
                                       showlegend=False), row=row, col=col)
                        self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=row, col=col)
                if isinstance(data, dict):
                    inner_keys = {}
                    for orbit, orbit_data in data.items():
                        col = self.orbits.index(orbit) + 1 if self.number_of_orbits > 1 else 1
                        if isinstance(orbit_data, dict):
                            
                            if len(self.data_integration.number_of_SAR_elements[technique]) == 1:
                                color_index = [0]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 2:
                                color_index = [0, 4]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 3:
                                color_index = [0, 4, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 4:
                                color_index = [0, 2, 4, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 5:
                                color_index = [0, 2, 4, 6, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 6:
                                color_index = [0, 1, 2, 4, 6, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 7:
                                color_index = [0, 1, 2, 3, 4, 6, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 8:
                                color_index = [0, 1, 2, 3, 4, 5, 6, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 9:
                                color_index = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                            elif len(self.data_integration.number_of_SAR_elements[technique]) == 10:
                                color_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                            
                            for _, (subkey, subdata) in enumerate(orbit_data.items()):
                                if subkey in inner_keys.keys():
                                    showlegend = False
                                else:
                                    showlegend = True
                                    inner_keys[subkey]=color_index[len(inner_keys)]
                                
                                color_for_data = data_colors[subdata.type][inner_keys[subkey]]
                                
                                rates = 1000 if subdata.type == "DInSAR" else 1
                                if subdata.type == "DInSAR":
                                    max_rate.extend([max(subdata.data["DSP"] * rates)])
                                    min_rate.extend([min(subdata.data["DSP"] * rates)])
                                else:
                                    max_disp["ver"].extend([max(subdata.data["DSP"] * rates)])
                                    min_disp["ver"].extend([min(subdata.data["DSP"] * rates)])

                                fig.add_trace(
                                    go.Scatter(x=subdata.data.index, y=subdata.data["DSP"] * rates, mode='markers',
                                               name=subdata.sublabel,
                                               showlegend=showlegend, legendgroup=subdata.type,
                                               legendgrouptitle_text=subdata.type,
                                               marker=dict(color=color_for_data, size = 8)), row=row, col=col)
                                self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=row, col=col)
                        else:
                            showlegend = True if self.orbits.index(orbit) == 0 else False
                            rates = 1000 if orbit_data.type == "DInSAR" else 1
                            if orbit_data.type == "DInSAR":
                                max_rate.extend([max(orbit_data.data["DSP"] * rates)])
                                min_rate.extend([min(orbit_data.data["DSP"] * rates)])
                            else:
                                max_disp["ver"].extend([max(orbit_data.data["DSP"] * rates)])
                                min_disp["ver"].extend([min(orbit_data.data["DSP"] * rates)])

                            fig.add_trace(
                                go.Scatter(x=orbit_data.data.index, y=orbit_data.data["DSP"] * rates, mode='markers',
                                           name='',
                                           showlegend=showlegend, legendgroup=orbit_data.type,
                                           legendgrouptitle_text=orbit_data.type,
                                           marker=dict(color=data_colors[orbit_data.type][0], size = 8)), row=row, col=col)
                            self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=row, col=col)
                    if technique == "DInSAR":
                        for orbit in set(self.orbits).difference(set(data.keys())):
                            col = self.orbits.index(orbit) + 1 if self.number_of_orbits > 1 else 1
                            fig.add_trace(
                                go.Scatter(x=dates_range, y=pd.Series(dtype=object), mode='markers',
                                           showlegend=False), row=row, col=col)
                            self.add_vline(fig, timestamp_min_value, timestamp_max_value, row=row, col=col)
        if self.data_integration.mean_data_dict.get("DInSAR") is not None:
            row = 4 if ("SBAS" in self.sar_data_types or "PSI" in self.sar_data_types) else 3
            for orbit, orbit_data in self.data_integration.mean_data_dict.get("DInSAR").items():
                col = self.orbits.index(orbit) + 1 if self.number_of_orbits > 1 else 1

                max_rate.extend([max(orbit_data['forward_mean'])])
                min_rate.extend([min(orbit_data['forward_mean'])])

                fig.add_trace(go.Scatter(x=orbit_data['forward_mean'].index, y=orbit_data['forward_mean'], mode='lines',
                                         name=name_forward, showlegend=False, legendgroup="kalman",
                                         line=dict(width=5, color=data_colors["forward"])), row=row, col=col)
                if orbit_data.get('backward_mean') is not None:
                    max_rate.extend([max(orbit_data['backward_mean'])])
                    min_rate.extend([min(orbit_data['backward_mean'])])

                    fig.add_trace(
                        go.Scatter(x=orbit_data['backward_mean'].index, y=orbit_data['backward_mean'], mode='lines',
                                   name=name_backward, showlegend=False, legendgroup="kalman",
                                   line=dict(width=4, color=data_colors["backward"])), row=row, col=col)

        if self.data_integration.mean_data_dict.get("SAR_SBAS_PSI_MEAN") is not None:
            row = 3
            for orbit, orbit_data in self.data_integration.mean_data_dict.get("SAR_SBAS_PSI_MEAN").items():
                col = self.orbits.index(orbit) + 1 if self.number_of_orbits > 1 else 1

                max_disp["ver"].extend([max(orbit_data['forward_mean'].dropna())])
                min_disp["ver"].extend([min(orbit_data['forward_mean'].dropna())])

                fig.add_trace(
                    go.Scatter(x=orbit_data['forward_mean'].dropna().index, y=orbit_data['forward_mean'].dropna(),
                               mode='lines', name=name_forward, showlegend=False, legendgroup="kalman",
                               line=dict(width=5, color=data_colors["forward"])), row=row, col=col)

                if orbit_data.get('backward_mean') is not None:
                    max_disp["ver"].extend([max(orbit_data['backward_mean'].dropna())])
                    min_disp["ver"].extend([min(orbit_data['backward_mean'].dropna())])

                    fig.add_trace(
                        go.Scatter(x=orbit_data['backward_mean'].dropna().index, y=orbit_data['backward_mean'].dropna(),
                                   mode='lines', name=name_backward, showlegend=False, legendgroup="kalman",
                                   line=dict(width=4, color=data_colors["backward"])), row=row, col=col)

        # ORDER OF TRACES FOR LEGEND
        new_data = [trace for trace in fig.data if trace.name != name_forward] + [trace for trace in fig.data if
                                                                                  trace.name == name_forward]
        new_data = [trace for trace in new_data if trace.name != name_backward] + [trace for trace in new_data if
                                                                                   trace.name == name_backward]
        fig.data = new_data

        # CREATE Y RANGE
        max_disp_ver = self.find_max_value(max_disp["ver"])
        max_disp_hor = self.find_max_value(max_disp["hor"])
        min_disp_ver = self.find_min_value(min_disp["ver"])
        min_disp_hor = self.find_min_value(min_disp["hor"])

        min_rate = self.find_min_value(min_rate)
        max_rate = self.find_max_value(max_rate)

        range_ver = [min_disp_ver - additional_range * abs(max_disp_ver - min_disp_ver),
                     max_disp_ver + additional_range * abs(max_disp_ver - min_disp_ver)]
        range_hor = [min_disp_hor - additional_range * abs(max_disp_hor - min_disp_hor),
                     max_disp_hor + additional_range * abs(max_disp_hor - min_disp_hor)]
        range_rate = [min_rate - additional_range * abs(max_rate - min_rate),
                      max_rate + additional_range * abs(max_rate - min_rate)]
        
        min_range_value = 0.05
        if min(range_ver[0], range_hor[0]) > -min_range_value and max(range_ver[1], range_hor[1]) < min_range_value:
            range_ver = [-min_range_value, min_range_value]
            range_hor = [-min_range_value, min_range_value]

        # UPDATE X AND Y RANGE FOR GNSS DISPLACEMENT    
        fig.update_yaxes(range=range_hor,   row=1, col=1)
        fig.update_yaxes(range=range_hor,   row=1, col=2)
        fig.update_yaxes(range=range_ver,   row=1, col=3)
        fig.update_xaxes(range=dates_range, row=1)
                    
        # UPDATE X AND Y RANGE FOR GNSS RATE
        fig.update_xaxes(range=dates_range, row=2)
        fig.update_yaxes(range=range_rate,  row=2)
        
        # UPDATE X AND Y RANGE FOR DInSAR OR PSI& SBAS
        fig.update_xaxes(range=dates_range, row=3)
        if rows == 4 and "DInSAR" in self.sar_data_types: 
            fig.update_yaxes(range=range_rate, row=3)
        else:
            fig.update_yaxes(range=range_ver,  row=3)
        
        # UPDATE X AND Y RANGE FOR DInSAR WITH PSI& SBAS
        fig.update_xaxes(range=dates_range, row=4)
        fig.update_yaxes(range=range_rate,  row=4)


        # UPDATE EVERY ANNOTATIONS -> FONT SIZE
        fig.update_annotations(font_size=24, font_color = 'black')

        layout_settings = {
            'title_text': f"MultiDEFusion: <b>{self.data_integration.station}</b>",
            'font': dict(family='Helvetica', size=20, color = 'black'),
            'height': 1400,
            'width': 1600,
            'showlegend': True,
            'margin' : dict(r=10,b=10),
            'legend': dict(orientation='h',
                           # groupclick="toggleitem",
                           itemsizing='constant',
                           bordercolor='black',
                           borderwidth=1,
                           yanchor="bottom",
                           y=vertical_postition['1'][1]+shift_legend,
                           xanchor="right",
                           x=1),
            'plot_bgcolor': 'white',
        }

        axis_settings = {
            'gridcolor': 'lightgray',
            'ticks': 'inside',
            'linecolor': 'black',
            'mirror': 'ticks',
            'color': 'black',
            'minor': dict(gridcolor='lightgray', gridwidth=0.1, ticks='inside', tickcolor='black'),
            'automargin': 'height+width+left+right',    
        }

        # UPDATE POSITION AND SETTINGS FOR GNSS DISPLACEMENT
        for i in range(1, 4):
            layout_settings[f'xaxis{i}'] = dict(domain=subplots_postition["3"][i - 1], showticklabels=False, hoverformat = '%d %b %Y',
                                                **axis_settings)
            layout_settings[f'yaxis{i}'] = dict(
                domain=vertical_postition['1'],
                title='<b>Displacement [m]</b>' if i == 1 else '',
                showticklabels=True if i == 1 or i == 3 else False,
                tickformat='.2f',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='lightgray',
                hoverformat = '.3f',
                **axis_settings
            )
        # UPDATE POSITION AND SETTINGS FOR GNSS RATE
        for i in range(1, 4):
            layout_settings[f'xaxis{i + 3}'] = dict(domain=subplots_postition["3"][i - 1],
                                                    showticklabels=True, tickformat='%b<br>%Y', hoverformat = '%d %b %Y', **axis_settings)
            layout_settings[f'yaxis{i + 3}'] = dict(
                domain=vertical_postition['2'],
                title='<b>Rate<br>[mm/day]</b>' if i == 1 else '',
                showticklabels=True if i == 1 or i == 3 else False,
                tickformat='.2f',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='lightgray',
                hoverformat = '.1f',
                **axis_settings
            )

        if self.number_of_orbits == 3:
            subplots_postition_orbits = str(self.number_of_orbits) + "*"
        else:
            subplots_postition_orbits = str(self.number_of_orbits)
            

        
        table_vertical  = table_postition['GNSS']
        table_title_pos = shift_title_fig*5
        picker_position = custom_position['GNSS']

        if rows == 4:
            if "DInSAR" in self.sar_data_types and len(self.sar_data_types) == 1:
                table_vertical  = table_postition['DInSAR']
                table_title_pos = shift_title_fig*5
                picker_position = custom_position['DInSAR']
                for i in range(1, len(self.orbits) + 1):
                    layout_settings[f'xaxis{i + 6}'] = dict(
                        domain=subplots_postition[subplots_postition_orbits][i - 1],
                        tickformat='%b<br>%Y', hoverformat = '%d %b %Y', **axis_settings)
                    layout_settings[f'yaxis{i + 6}'] = dict(
                        domain=vertical_postition['3*'],
                        title='<b>Rate<br>[mm/day]</b>' if i == 1 else '',
                        showticklabels=True if i == 1 else False,
                        tickformat='.2f',
                        zeroline=True,
                        zerolinewidth=2,
                        zerolinecolor='lightgray',
                        hoverformat = '.1f',
                        **axis_settings
                    )

        if rows == 4:
            if "DInSAR" not in self.sar_data_types and len(self.sar_data_types) > 0:
                table_vertical  = table_postition['SBAS']
                table_title_pos = shift_title_fig
                picker_position = custom_position['SBAS']
                for i in range(1, len(self.orbits) + 1):
                    layout_settings[f'xaxis{i + 6}'] = dict(
                        domain=subplots_postition[subplots_postition_orbits][i - 1],
                        tickformat='%b<br>%Y', hoverformat = '%d %b %Y', **axis_settings)
                    layout_settings[f'yaxis{i + 6}'] = dict(
                        domain=vertical_postition['3'],
                        title='<b>Displacement [m]</b>' if i == 1 else '',
                        showticklabels=True if i == 1 else False,
                        tickformat='.2f',
                        zeroline=True,
                        zerolinewidth=2,
                        zerolinecolor='lightgray',
                        hoverformat = '.3f',
                        **axis_settings
                    )

        if rows == 5:
            table_vertical  = table_postition['MSAR']
            table_title_pos = shift_title_fig
            picker_position = custom_position['MSAR']
            for i in range(1, len(self.orbits) + 1):
                layout_settings[f'xaxis{i + 6}'] = dict(domain=subplots_postition[subplots_postition_orbits][i - 1],
                                                        showticklabels=False, hoverformat = '%d %b %Y', **axis_settings)
                layout_settings[f'yaxis{i + 6}'] = dict(
                    domain=vertical_postition['3'],
                    title='<b>Displacement [m]</b>' if i == 1 else '',
                    showticklabels=True if i == 1 else False,
                    tickformat='.2f',
                    zeroline=True,
                    zerolinewidth=2,            
                    zerolinecolor='lightgray',
                    hoverformat = '.3f',
                    **axis_settings
                )
                layout_settings[f'xaxis{i + 6 + len(self.orbits)}'] = dict(
                    domain=subplots_postition[subplots_postition_orbits][i - 1],
                    tickformat='%b<br>%Y', hoverformat = '%d %b %Y', **axis_settings)
                layout_settings[f'yaxis{i + 6 + len(self.orbits)}'] = dict(
                    domain=vertical_postition['4'],
                    title='<b>Rate<br>[mm/day]</b>' if i == 1 else '',
                    showticklabels=True if i == 1 else False,
                    tickformat='.2f',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='lightgray',
                    hoverformat = '.1f',
                    **axis_settings
                )

        fig.update_layout(**layout_settings)

        fig.update_layout(xaxis=dict(matches='x'),
                          xaxis4=dict(matches='x'),
                          xaxis2=dict(matches='x2'),
                          xaxis5=dict(matches='x2'),
                          xaxis3=dict(matches='x3'),
                          xaxis6=dict(matches='x3'),
                          hovermode='x unified',
                          )
        
        fig.update_traces(hovertemplate='%{y} %{xother}')
        
        if self.data_integration.backward_df_xe is not None:
            max_total_values = self.find_max_total(self.data_integration.backward_df_xe)
            mean_rate = self.data_integration.backward_df_xe.mean()
            kalman_col = '  Kalman<br>Backward'
        else:
            kalman_col = ' Kalman<br>Forward'
            max_total_values = self.find_max_total(self.data_integration.forward_df_xe)
            mean_rate = self.data_integration.forward_df_xe.mean()
        
       
        fig.add_trace(go.Table(
            header=dict(values=[f"{kalman_col}", '     Max<br>  DEF [m]',  'Mean rate<br>  [m/year]'],
                        align='center',
                        fill_color = 'rgb(189, 215, 231)',
                        line_color='black',
                        font = dict(color = 'black', size = 24)),
            cells =dict(values=[['North', 'East', 'Up'], max_total_values[disp_cols].apply(lambda x: f'{x:.3f}'), (mean_rate[rate_cols]*365.25).apply(lambda x: f'{x:.3f}')], 
                        align='center', 
                        height=41.5,
                        fill_color = 'white',
                        line_color='black',
                        font = dict(color = 'black', size = 24))
            ), row=rows, col=1)
                                
        fig.update_traces(
            domain={'y': table_vertical, 'x': subplots_postition['3'][1]},
            selector={'type': 'table'})

        for annotation, domain in zip(fig['layout']['annotations'][:3], subplots_postition["3"]):
            annotation['x'] = (domain[0] + domain[1]) / 2
            annotation['y'] = vertical_postition['1'][1]+shift_title_fig

        if self.number_of_orbits == 3:
            subplots_pos = subplots_postition["3*"]
        elif self.number_of_orbits in [1, 2]:
            subplots_pos = subplots_postition[str(self.number_of_orbits)]
            
        if rows > 3:
            for annotation, domain in zip(fig['layout']['annotations'][3:], subplots_pos):
                annotation['x'] = (domain[0] + domain[1]) / 2
                annotation['y'] = vertical_postition['3'][1]+shift_title_fig
                
        fig.add_annotation(
            x = mean(subplots_postition['3'][1]),
            y = table_vertical[1]+table_title_pos,
            xref = "paper",
            yref = "paper",
            showarrow=False,
            font_size = 25,
            font_color = 'black',
            text = "<b>Relevant values</b>")
        
        fig.add_annotation(
            x = mean(subplots_postition['3'][1]),
            y = 0.005,
            xref = "paper",
            yref = "paper",
            showarrow=False,
            font_family = 'Helvetica',
            font_size = 15,
            font_color = 'black',
            text = "The Kalman filter displacements and rates shown for InSAR orbits in the Line of Sight (LOS) domain were determined based on the mean heading and incidence angle values.")
        
        #DASH PART
        app = dash.Dash(__name__)
        container1 = html.Div([
            dcc.Graph(
                id='subplot-graph',
                figure = fig,
                config = {
                    'toImageButtonOptions': {'format': 'svg', 'filename': 'MultiDEFusion_'+self.data_integration.station},
                    'displaylogo': False,
                    'showEditInChartStudio': True,
                    'plotlyServerURL': "https://chart-studio.plotly.com",
                    'modeBarButtonsToRemove': ['select', 'lasso2d', 'autoScale'],
                    'modeBarButtonsToAdd': ['drawline', 'drawcircle', 'drawrect', 'eraseshape', 'sendDataToCloud']
                    }
                ),
            ])
        
        container2 = html.Div([
            html.H2('Customise dates range',
                    style={'fontsize': '25px',
                           'margin-bottom': '5px',
                           'margin-left': '65px',}),
            
		    dcc.DatePickerRange(
				id='date_range',
				display_format='DD/MM/YYYY',
				show_outside_days = True,
				start_date=dates_range[0],
				end_date=dates_range[1],
                number_of_months_shown=2,
                style={'border': '2px solid black',
                       'margin-bottom': '10px',
                       'vertical-align': 'middle',
                       'display': 'inline-block'},
			),
            
            html.Button('Restore default',
                        id='reset_dates',
                        n_clicks=0,
                        style={'fontsize': '20px',
                               'font-weight': 'bold',
                               'height': '45px', 
                               'width': '100px', 
                               'margin-left': '10px',
                               'margin-bottom': '10px',
                               'vertical-align': 'middle',
                               'display': 'inline-block'}),
            
            html.Div(id='output_x_range',
                     style={'fontsize': '15px',
                            'color': 'red'}),
            
            html.H2('Customise values range',
                    style={'fontsize': '25px',
                           'margin-bottom': '5px',
                           'margin-left': '60px'}),
                                     
            html.Div([
            dcc.Dropdown(
                id = 'show_or_hide',
                options=[
                    {'label': 'Horizontal range [m]', 'value': 'hor'},
                    {'label': 'Vertical & LOS range [m]', 'value': 'ver'},
                    {'label': 'Rate range [mm/day]', 'value': 'rate'}],
                value = 'hor',
                clearable = False,
                style={'width': '286px',
                       'font-size': '20px', 
                       'border': '0.2px solid black',
                       'border-radius': '0',
                       'height': '40px', 
                       'vertical-align': 'middle',
                       'display': 'inline-block'},
            ),
            
            html.Button('Sync ranges',
                        id='fit_ranges',
                        n_clicks=0,
                        style={'fontsize': '20px',
                               'font-weight': 'bold',
                               'height': '38px', 
                               'width': '100px',
                               'margin-left': '10px',
                               'vertical-align': 'middle',
                               'display': 'inline-block'}
            ),
            ]),

            html.Div([
                html.Div(id = 'hor_options', children=[
                dcc.Input(
                id = 'hor_min',
                placeholder = 'Minimum value',
                type='number',
                step = 0.001,
                value = float("{:.3f}".format(range_hor[0])),
                style = {'font-size': '17px',
                         'border': '1px solid black',
                         'height': '30px', 
                         'width': '138px'}
                ),
            
                dcc.Input(
                id = 'hor_max',
                placeholder = 'Maximum value',
                type='number',
                step = 0.001,
                value = float("{:.3f}".format(range_hor[1])),
                style = {'font-size': '17px',
                         'border': '1px solid black',
                         'height': '30px', 
                         'width': '138px'}
                )
            ],
            style={'display': 'block',
                   'margin-top': '5px',
                   'margin-bottom': '10px'},
            ),
            
            html.Div(id = 'ver_options', children=[
                dcc.Input(
                id = 'ver_min',
                placeholder = 'Minimum value',
                type='number',
                step = 0.001,
                value = float("{:.3f}".format(range_ver[0])),
                style = {'font-size': '17px',
                         'border': '1px solid black',
                         'height': '30px', 
                         'width': '138px'}
                ),
                
                dcc.Input(
                id = 'ver_max',
                placeholder = 'Maximum value',
                type='number',
                step = 0.001,
                value = float("{:.3f}".format(range_ver[1])),
                style = {'font-size': '17px',
                         'border': '1px solid black',
                         'height': '30px', 
                         'width': '138px'}
                )
            ],
            style={'display': 'block',
                   'margin-bottom': '10px'},
            ),
            
            html.Div(id = 'rate_options', children=[
                dcc.Input(
                id = 'rate_min',
                placeholder = 'Minimum value',
                type='number',
                step = 0.1,
                value = float("{:.1f}".format(range_rate[0])),
                style = {'font-size': '17px',
                         'border': '1px solid black',
                         'height': '30px', 
                         'width': '138px'}
                ),
                
                dcc.Input(
                id = 'rate_max',
                placeholder = 'Maximum value',
                type='number',
                step = 0.1,
                value = float("{:.1f}".format(range_rate[1])),
                style = {'font-size': '17px', 
                         'border': '1px solid black',
                         'height': '30px', 
                         'width': '138px'}
                ),
                
            ],
            style={'display': 'block',
                   'margin-bottom': '10px'},
            )
            ], style={'display': 'inline-block',
                      'vertical-align': 'middle'}),

            
            html.Button('Restore default',
                        id='reset_values',
                        n_clicks=0,
                        style={'fontsize': '20px',
                               'font-weight': 'bold',
                               'height': '38px', 
                               'width': '100px',
                               'margin-left': '10px',
                               'display': 'inline-block',
                               'vertical-align': 'middle',}
            ),
            
            
            html.Div(id='output_y_range',
                     style={'fontsize': '15px',
                            'color': 'red'}
                     ),
        ], 
        style={'position': 'absolute', 
               'top': f'{picker_position}px', 
               'left': '145px', 
               'width': 'fit-content',
               'fontFamily': 'Helvetica',
               'color': 'black', 
               }
        )
        
        app.layout = html.Div([container1, container2])
		
        @app.callback(
            Output('hor_options', 'style'),
            Output('ver_options', 'style'),
            Output('rate_options', 'style'),
            Input('show_or_hide', 'value'))

        def show_hide_element(visibility_state):
            if visibility_state == 'hor':
                return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
            elif visibility_state == 'ver':
                return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
            else:
                return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    
        @app.callback(
           Output('subplot-graph', 'figure'),
           Output('output_x_range', 'children'),
           Output('output_y_range', 'children'),
           [Input('date_range', 'start_date'),
            Input('date_range', 'end_date'),
            Input('hor_min', 'value'), 
            Input('hor_max', 'value'),
            Input('ver_min', 'value'), 
            Input('ver_max', 'value'),
            Input('rate_min', 'value'), 
            Input('rate_max', 'value')]
           )

        def update_subplot(start_date, end_date, hor_min, hor_max, ver_min, ver_max, rate_min, rate_max):

            warning_dates = None
            if end_date <= start_date and end_date is not None and start_date is not None:
                warning_dates = 'The end date must be greater than the start date!'
            if warning_dates == None:
                fig.update_xaxes(range=(start_date, end_date))

            warning_values = None
            if hor_min is not None and hor_max is not None and hor_max <= hor_min:
                warning_values = 'Maximum value must be greater than minimum!'
            if ver_min is not None and ver_max is not None and ver_max <= ver_min:
                warning_values = 'Maximum value must be greater than minimum!'
            if rate_min is not None and rate_max is not None and rate_max <= rate_min:
                warning_values = 'Maximum value must be greater than minimum!'
            if warning_values == None:                
                # UPDATE Y RANGE FOR GNSS DISPLACEMENT    
                fig.update_yaxes(range=[hor_min, hor_max], row=1, col=1)
                fig.update_yaxes(range=[hor_min, hor_max], row=1, col=2)
                fig.update_yaxes(range=[ver_min, ver_max], row=1, col=3)
                            
                # UPDATE X AND Y RANGE FOR GNSS RATE
                fig.update_yaxes(range=[rate_min, rate_max], row=2)
                
                # UPDATE X AND Y RANGE FOR DInSAR OR PSI & SBAS
                if rows == 4 and "DInSAR" in self.sar_data_types: 
                    fig.update_yaxes(range=[rate_min, rate_max], row=3)
                else:
                    fig.update_yaxes(range=[ver_min, ver_max], row=3)
                
                # UPDATE X AND Y RANGE FOR DInSAR WITH PSI& SBAS
                fig.update_yaxes(range=[rate_min, rate_max], row=4)
        
            return fig, warning_dates, warning_values
        

        @app.callback(
            Output('date_range', 'start_date'),
            Output('date_range', 'end_date'),
            Input('reset_dates', 'n_clicks')
        )
        
        def reset_date_range(n_clicks):
            return dates_range[0], dates_range[1]
        
        @app.callback(
          [Output('hor_min', 'value'), 
            Output('hor_max', 'value'),
            Output('ver_min', 'value'), 
            Output('ver_max', 'value'),
            Output('rate_min', 'value'), 
            Output('rate_max', 'value')],
            Input('reset_values', 'n_clicks'),
            Input('fit_ranges', 'n_clicks'),
            prevent_initial_call=True
          )
        
        def reset_fit_range(btn1, btn2):
            min_range = float("{:.3f}".format(min(range_ver[0], range_hor[0])))
            max_range = float("{:.3f}".format(max(range_ver[1], range_hor[1])))
            if 'reset_values' == ctx.triggered_id:
                return float("{:.3f}".format(range_hor[0])), float("{:.3f}".format(range_hor[1])), float("{:.3f}".format(range_ver[0])), float("{:.3f}".format(range_ver[1])),  float("{:.1f}".format(range_rate[0])), float("{:.1f}".format(range_rate[1]))
            if 'fit_ranges' == ctx.triggered_id:
                return min_range, max_range, min_range, max_range, float("{:.1f}".format(range_rate[0])), float("{:.1f}".format(range_rate[1]))
       
        
        print("MultiDEFusion procedure accomplished.\n")
        app.run_server(debug=True, host="localhost", port=self.data_integration.port);
        webbrowser.open(f'http://localhost:{self.data_integration.port}')