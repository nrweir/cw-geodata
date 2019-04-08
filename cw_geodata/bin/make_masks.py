import argparse
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from cw_geodata.vector_label.polygon import geojson_to_px_gdf
from cw_geodata.vector_label.polygon import georegister_px_df
from itertools import repeat


def main():

    parser = argparse.ArgumentParser(
        description='Create training pixel masks from vector data',
        argument_default=None)

    parser.add_argument('--source_file', '-s', type=str,
                        help='Full path to file to create mask from.')
    parser.add_argument('--reference_image', '-r', type=str,
                        help='Full path to a georegistered image in the same' +
                        ' coordinate system (for conversion to pixels) or in' +
                        ' the target coordinate system (for conversion to a' +
                        ' geographic coordinate reference system).')
    parser.add_argument('--output_path', '-o', type=str,
                        help='Full path to the output file for the converted' +
                        'footprints.')
    parser.add_argument('--geometry_column', '-g', type=str,
                        default='geometry', help='The column containing' +
                        ' footprint polygons to transform. If not provided,' +
                        ' defaults to "geometry".')
    parser.add_argument('--transform', '-t', action='store_true',
                        default=False, help='Use this flag if the geometries' +
                        ' are in a georeferenced coordinate system and' +
                        ' need to be converted to pixel coordinates.')
    parser.add_argument('--value', '-v', type=int, help='The value to set' +
                        ' for labeled pixels in the mask. Defaults to 255.')
    parser.add_argument('--value_column', '-vc', type=str, help='The column' +
                        ' in the source file that defines value per object.' +
                        ' only effects the footprint mask, not edges or' +
                        ' contacts. If provided, --value is ignored.')
    parser.add_argument('--footprint', '-f', action='store_true',
                        default=False, help='If this flag is set, the mask' +
                        ' will include filled-in building footprints as a' +
                        ' channel.')
    parser.add_argument('--edge', '-e', action='store_true',
                        default=False, help='If this flag is set, the mask' +
                        ' will include the building edges as a channel.')
    parser.add_argument('--edge_width', '-ew', type=int,
                        help='Pixel thickness of the edges in the edge mask.' +
                        ' Defaults to 3 if not provided.')
    parser.add_argument('--edge_type', '-et', type=str,
                        help='Type of edge: either inner or outer. Defaults' +
                        ' to inner if not provided.')
    parser.add_argument('--contact', '-c', action='store_true',
                        default=False, help='If this flag is set, the mask' +
                        ' will include contact points between buildings as a' +
                        ' channel.')
    parser.add_argument('--contact_spacing', '-cs', type=int, help='Sets the' +
                        ' maximum distance between two buildings, in source' +
                        ' file units, that will be identified as a contact.' +
                        ' Defaults to 10.')
    parser.add_argument('--batch', '-b', action='store_true', default=False,
                        help='Use this flag if you wish to operate on' +
                        ' multiple files in batch. In this case,' +
                        ' --argument-csv must be provided. See help' +
                        ' for --argument_csv and the codebase docs at' +
                        ' https://cw-geodata.readthedocs.io for more info.')
    parser.add_argument('--argument_csv', '-a', type=str,
                        help='The reference file for variable values for' +
                        ' batch processing. It must contain columns to pass' +
                        ' the source_file and reference_image arguments, and' +
                        ' can additionally contain columns providing the' +
                        ' footprint_column and decimal_precision arguments' +
                        ' if you wish to define them differently for items' +
                        ' in the batch. These columns must have the same' +
                        ' names as the corresponding arguments. See the ' +
                        ' usage recipes at https://cw-geodata.readthedocs.io' +
                        ' for examples.')
    parser.add_argument('--workers', '-w', type=int, default=1,
                        help='The number of parallel processing workers to' +
                        ' use. This should not exceed the number of CPU' +
                        ' cores available.')

    args = parser.parse_args()
