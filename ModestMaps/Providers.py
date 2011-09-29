import re
from math import pi, pow

from Core import Coordinate
from Geo import LinearProjection, MercatorProjection, deriveTransformation

ids = ('MICROSOFT_ROAD', 'MICROSOFT_AERIAL', 'MICROSOFT_HYBRID',
       'YAHOO_ROAD',     'YAHOO_AERIAL',     'YAHOO_HYBRID',
       'BLUE_MARBLE',
       'OPEN_STREET_MAP')

class IMapProvider:
    def __init__(self):
        raise NotImplementedError("Abstract method not implemented by subclass.")
        
    def getTileUrls(self, coordinate):
        raise NotImplementedError("Abstract method not implemented by subclass.")

    def getTileUrls(self, coordinate):
        raise NotImplementedError("Abstract method not implemented by subclass.")

    def tileWidth(self):
        raise NotImplementedError("Abstract method not implemented by subclass.")
    
    def tileHeight(self):
        raise NotImplementedError("Abstract method not implemented by subclass.")
    
    def locationCoordinate(self, location):
        return self.projection.locationCoordinate(location)

    def coordinateLocation(self, location):
        return self.projection.coordinateLocation(location)

    def sourceCoordinate(self, coordinate):
        raise NotImplementedError("Abstract method not implemented by subclass.")

    def sourceCoordinate(self, coordinate):
        wrappedColumn = coordinate.column % pow(2, coordinate.zoom)
        
        while wrappedColumn < 0:
            wrappedColumn += pow(2, coordinate.zoom)
            
        return Coordinate(coordinate.row, wrappedColumn, coordinate.zoom)

class TemplatedMercatorProvider(IMapProvider):
    """ Convert URI templates into tile URLs, using a tileUrlTemplate identical to:
        http://code.google.com/apis/maps/documentation/overlays.html#Custom_Map_Types
        
        By passing in "tms" as the scheme, you can render tiles whose coordinates start (0, 0) in the lower left and not the top-left
        http://wiki.openstreetmap.org/wiki/GIS_for_Dummies_(written_by_a_dummy)#TMS_.28Tile_Map_Service.29
        http://mapbox.com/wax/
    """
    def __init__(self, template, scheme="xyz"):
        # the spherical mercator world tile covers (-π, -π) to (π, π)
        t = deriveTransformation(-pi, pi, 0, 0, pi, pi, 1, 0, -pi, -pi, 0, 1)
        self.projection = MercatorProjection(0, t)
        self.scheme = scheme
        self.templates = []
        
        while template:
            match = re.match(r'^(http://\S+?)(,http://\S+)?$', template)
            first = match.group(1)
            
            if match:
                # normalize {x}{y}{z} to {X}{Y}{Z}
                first = re.sub("{[xyz]}", lambda mo: mo.group(0).upper(), first)
                self.templates.append(first)
                template = template[len(first):].lstrip(',')
            else:
                break

    def tileWidth(self):
        return 256

    def tileHeight(self):
        return 256

    def getTileUrls(self, coordinate):
        x, y, z = str(int(coordinate.column)), str(int(coordinate.row)), str(int(coordinate.zoom))
        if self.scheme == "tms":
            y = str(int(pow(2, int(coordinate.zoom)) - int(coordinate.row) - 1))
        return [t.replace('{X}', x).replace('{Y}', y).replace('{Z}', z) for t in self.templates]        