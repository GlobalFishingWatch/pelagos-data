import gdal
import ogr
import osr
import struct
import shapely
import pyproj

strctypes = {
    gdal.GDT_Byte: "c",
    gdal.GDT_Float32: "f",
    gdal.GDT_Float64: "d",
    gdal.GDT_Int16: "h",
    gdal.GDT_Int32: "i",
    gdal.GDT_UInt16: "H",
    gdal.GDT_UInt32: "I"
}


gdal.UseExceptions()

def wktToProj(proj):
    conv = osr.SpatialReference()
    conv.ImportFromWkt(proj)
    return conv.ExportToProj4()

class PixelReader(object):
    def __init__(self, filename):
        self.filename = filename
        self.dataset = gdal.Open(self.filename) 
        self.proj = pyproj.Proj(wktToProj(self.dataset.GetProjection()))
        self.trans = self.dataset.GetGeoTransform()

        self.rasterBand = self.dataset.GetRasterBand(1)
        self.noDataValue = self.rasterBand.GetNoDataValue()



    def transform(self, x, y):
        # Calculates inverse of (1, x, y) = (1, p, l) * self.trans
        #
        # calculated using sympy:
        # t0,t1,t2,t3,t4,t5 = sympy.symbols("t_0,t_1,t_2,t_3,t_4,t_5")
        # p,l,x, y = sympy.symbols("p,l,x,y")
        # M = sympy.Matrix([[1, t0, t3], [0, t1, t4], [0, t2, t5]]).inv()
        # e = sympy.Matrix([[1, x, y]]) * M
        # print e.tolist()[0][1]
        # print e.tolist()[0][2]

        t = self.trans
        
        p = (-t[0]/t[1]
             + x*(1/t[1] + t[2]*t[4]/(t[1]**2*(t[5] - t[2]*t[4]/t[1])))
             - t[2]*y/(t[1]*(t[5] - t[2]*t[4]/t[1]))
             + t[2]*(-t[0]*t[4]/t[1] + t[3])/(t[1]*(t[5] - t[2]*t[4]/t[1])))
        l = (y/(t[5] - t[2]*t[4]/t[1])
             - (-t[0]*t[4]/t[1] + t[3])/(t[5] - t[2]*t[4]/t[1])
             - t[4]*x/(t[1]*(t[5] - t[2]*t[4]/t[1])))

        return p, l

    def read(self, lon, lat):
        px, py = self.transform(*self.proj(lon, lat))
        px = int(px)
        py = int(py)

        structval = self.rasterBand.ReadRaster(px, py, 1, 1, buf_type=self.rasterBand.DataType)
        val = struct.unpack(strctypes[self.rasterBand.DataType], structval)[0]
        if val == self.noDataValue: val = None
        return val
