import os
import pandas as pd
from affine import Affine
from shapely.geometry import Polygon
from shapely.wkt import loads, dumps
from cw_geodata.data import data_dir
from cw_geodata.vector_label.polygon import convert_poly_coords, \
    affine_transform_gdf

square = Polygon([(10, 20), (10, 10), (20, 10), (20, 20)])
forward_result = loads("POLYGON ((733606 3725129, 733606 3725134, 733611 3725134, 733611 3725129, 733606 3725129))")
reverse_result = loads("POLYGON ((-1467182 7450238, -1467182 7450258, -1467162 7450258, -1467162 7450238, -1467182 7450238))")
# note that the xform below is the same as in cw_geodata/data/sample_geotiff.tif
aff = Affine(0.5, 0.0, 733601.0, 0.0, -0.5, 3725139.0)
affine_list = [0.5, 0.0, 733601.0, 0.0, -0.5, 3725139.0]
long_affine_list = [0.5, 0.0, 733601.0, 0.0, -0.5, 3725139.0,
                    0.0, 0.0, 1.0]
gdal_affine_list = [733601.0, 0.5, 0.0, 3725139.0, 0.0, -0.5]


class TestConvertPolyCoords(object):
    """Test the convert_poly_coords functionality."""

    def test_square_pass_affine(self):
        """Test both forward and inverse affine transforms when passed affine obj."""
        xform_result = convert_poly_coords(square, affine_obj=aff)
        assert xform_result == forward_result
        rev_xform_result = convert_poly_coords(square,
                                                affine_obj=aff,
                                                inverse=True)
        assert rev_xform_result == reverse_result

    def test_square_pass_raster(self):
        """Test forward affine transform when passed a raster reference."""
        raster_src = os.path.join(data_dir, 'sample_geotiff.tif')
        xform_result = convert_poly_coords(square, raster_src=raster_src)
        assert xform_result == forward_result

    def test_square_pass_list(self):
        """Test forward and reverse affine transform when passed a list."""
        fwd_xform_result = convert_poly_coords(square,
                                               affine_obj=affine_list)
        assert fwd_xform_result == forward_result
        rev_xform_result = convert_poly_coords(square,
                                               affine_obj=affine_list,
                                               inverse=True)
        assert rev_xform_result == reverse_result

    def test_square_pass_gdal_list(self):
        """Test forward affine transform when passed a list in gdal order."""
        fwd_xform_result = convert_poly_coords(square,
                                               affine_obj=gdal_affine_list
                                               )
        assert fwd_xform_result == forward_result

    def test_square_pass_long_list(self):
        """Test forward affine transform when passed a full 9-element xform."""
        fwd_xform_result = convert_poly_coords(
            square, affine_obj=long_affine_list
            )
        assert fwd_xform_result == forward_result


class TestAffineTransformGDF(object):
    """Test the affine_transform_gdf functionality."""

    def test_transform_csv(self):
        truth_gdf = pd.read_csv(os.path.join(data_dir, 'aff_gdf_result.csv'))
        input_df = os.path.join(data_dir, 'sample.csv')
        output_gdf = affine_transform_gdf(input_df, aff,
                                          geom_col="PolygonWKT_Pix",
                                          precision=0)
        output_gdf['geometry'] = output_gdf['geometry'].apply(dumps, trim=True)
        assert output_gdf.equals(truth_gdf)
