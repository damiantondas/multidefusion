# Output

The MultiDEFusion final output can be divided into two parts: Graphic and Dataset

## Graphic part

The final plot is created involving the [Plotly](https://plotly.com/) library and [Dash](https://dash.plotly.com/) framework. The graphic representation of the results is automatically launched on the localhost server on port 8050.

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
    - Download plot: To save the plot in **svg** format after user's manipulations.
    - Edit in Chart Studio: To provide more advanced modifications in the plotly [Chart Studio](https://chart-studio.plotly.com).
    - Zoom: Work for a selected part of the trace. Double click on the trace to zoom back out.
    - Pan: Working within a single trace by moving the current view of the trace.
    - Draw line: Working within a single trace.
    - Draw circle: Working within a single trace.
    - Draw rectangle: Working within a single trace.
    - Erase the active shape: A single-click to activate the shape.
    - Zoom in: Work simultaneously for all of the traces.
    - Zoom out: Work simultaneously for all of the traces.
    - Reset axes: Work simultaneously for all of the traces.

## Dataset part

The MultDEFusion library returns a dataset of time series for a particular station.

The collection of data is stored in the dictionary, where the key is the signature of station, and the value is the containing the dataset of time series.
