def classFactory(iface):
    from .road_shortest_path import RoadShortestPathPlugin
    return RoadShortestPathPlugin(iface)
