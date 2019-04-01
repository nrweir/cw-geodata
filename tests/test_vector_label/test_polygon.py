import os
from affine import Affine
from shapely.geometry import Polygon
from shapely.wkt import loads
from cw_geodata.data import data_dir
from cw_geodata.vector_label.polygon import convert_poly_coords


class TestConvertPolyCoords(object):
    """Test the convert_poly_coords functionality."""
    def __init__(self):
        self.square = Polygon([(10, 20), (10, 10), (20, 10), (20, 20)])
        self.forward_result = loads("POLYGON ((733606 3725129, 733606 3725134, 733611 3725134, 733611 3725129, 733606 3725129))")
        self.reverse_result = loads("POLYGON ((-1467182 7450238, -1467182 7450258, -1467162 7450258, -1467162 7450238, -1467182 7450238))")
        # note that the xform below is the same as in cw_geodata/data/sample_geotiff.tif
        self.aff = Affine(0.5, 0.0, 733601.0, 0.0, -0.5, 3725139.0)
        self.affine_list = [0.5, 0.0, 733601.0, 0.0, -0.5, 3725139.0]
        self.long_affine_list = [0.5, 0.0, 733601.0, 0.0, -0.5, 3725139.0,
                                 0.0, 0.0, 1.0]
        self.gdal_affine_list = [933601.0, 0.5, 0.0, 3725139.0, 0.0, -0.5]

    def test_square_pass_affine(self):
        """Test both forward and inverse affine transforms when passed affine obj."""
        xform_result = convert_poly_coords(self.square, affine_obj=self.aff)
        assert xform_result == self.forward_result
        rev_xform_result = convert_poly_coords(self.square,
                                                affine_obj=self.aff,
                                                inverse=True)
        assert rev_xform_result == self.reverse_result

    def test_square_pass_raster(self):
        """Test forward affine transform when passed a raster reference."""
        raster_src = os.path.join(data_dir, 'sample_geotiff.tif')
        xform_result = convert_poly_coords(self.square, raster_src=raster_src)
        assert xform_result == self.forward_result

    def test_square_pass_list(self):
        """Test forward and reverse affine transform when passed a list."""
        fwd_xform_result = convert_poly_coords(self.square,
                                               affine_obj=self.affine_list)
        assert fwd_xform_result == self.forward_result
        rev_xform_result = convert_poly_coords(self.square,
                                               affine_obj=self.affine_list,
                                               inverse=True)
        assert rev_xform_result == self.reverse_result

    def test_square_pass_gdal_list(self):
        """Test forward affine transform when passed a list in gdal order."""
        fwd_xform_result = convert_poly_coords(self.square,
                                               affine_obj=self.gdal_affine_list
                                               )
        assert fwd_xform_result == self.forward_result

    def test_square_pass_long_list(self):
        """Test forward affine transform when passed a full 9-element xform."""
        fwd_xform_result = convert_poly_coords(
            self.square, affine_obj=self.long_affine_list
            )
        assert fwd_xform_result == self.forward_result
