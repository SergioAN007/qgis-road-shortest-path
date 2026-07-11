# Road Shortest Path

A QGIS plugin for interactive shortest path routing on vector road networks.

The plugin allows you to calculate the shortest route between two points by simply clicking on the map. It automatically snaps the selected points to the nearest road and computes the optimal route using Dijkstra's algorithm.

## Features

* Interactive routing directly on the map
* Two-click route creation
* Automatic snapping to the nearest road
* Shortest path calculation using Dijkstra's algorithm
* Customizable route color
* Start and end markers
* Route length calculation
* Supports any LineString road network layer
* Persistent plugin settings

## Requirements

* QGIS 3.22 or newer

## Installation

### From ZIP

1. Open **Plugins → Manage and Install Plugins**.
2. Click **Install from ZIP**.
3. Select the plugin ZIP file.
4. Restart QGIS if necessary.

## Usage

1. Open your project containing a road network layer.
2. Click **Road Shortest Path** on the toolbar.
3. Select the road layer.
4. Click the first point on the map.
5. Click the destination point.
6. The shortest route will be generated automatically.

## Supported road layers

The plugin works with vector line layers representing road networks.

Supported providers include:

* Shapefile
* GeoPackage
* PostGIS
* Memory layers
* Any QGIS LineString vector layer

## Output

The plugin creates a **Road Shortest Path** group containing:

* Route
* Markers

The route can be edited, styled, exported, or saved like any other QGIS vector layer.


## License

MIT License.

## Author

Sergey

## Contributing

Issues and pull requests are welcome.

If you find a bug or have an idea for improvement, please open an issue.
