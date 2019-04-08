import argparse
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from cw_geodata.vector_label.mask import df_to_px_mask
from cw_geodata.utils.cli import _func_wrapper
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

    if args.batch is not None and args.argument_csv is None:
        raise ValueError(
            'To perform batch processing, you must provide both --batch and' +
            ' --argument_csv.')
    if args.argument_csv is None and args.source_file is None:
        raise ValueError(
            'You must provide a source file using either --source_file or' +
            ' --argument_csv.')
    if args.argument_csv is None and args.reference_image is None:
        raise ValueError(
            'You must provide a reference image using either' +
            ' --reference_image or --argument_csv.')
    if not args.footprint and not args.edge and not args.contact:
        raise ValueError(
            'You must specify --footprint, --edge, and/or --contact. See' +
            ' make_masks --help or the CLI documentation at' +
            ' cw-geodata.readthedocs.io.')

    if args.argument_csv is not None:
        arg_df = pd.read_csv(args.argument_csv)
    else:
        arg_df = pd.DataFrame({})

    # generate the channels argument for df_to_px_mask
    channels = []
    if args.footprint:
        channels.append('footprint')
    if args.edge:
        channels.append('boundary')
    if args.contact:
        channels.append('contact')
    if len(arg_df) < 2:
        arg_df['channels'] = channels
    else:
        arg_df['channels'] = [channels]*len(arg_df)  # all channels in each row

    if args.source_file is not None:
        arg_df['source_file'] = args.source_file
    if args.reference_image is not None:
        arg_df['reference_image'] = args.reference_image
    if args.output_path is not None and not args.batch:
        arg_df['output_path'] = args.output_path
    if args.geometry_column is not None:
        arg_df['geometry_column'] = args.geometry_column
    if args.transform:
        arg_df['transform'] = True
    if args.value is not None:
        arg_df['value'] = args.value
    if args.edge_width is not None:
        arg_df['edge_width'] = args.edge_width
    if args.edge_type is not None:
        arg_df['edge_type'] = args.edge_type
    if args.contact_spacing is not None:
        arg_df['contact_spacing'] = args.contact_spacing

    # rename arguments to match API
    arg_df = arg_df.rename(columns={'source_file': 'df',
                                    'output_path': 'out_file',
                                    'reference_image': 'reference_im',
                                    'geometry_column': 'geom_col',
                                    'transform': 'do_transform',
                                    'value': 'burn_value',
                                    'edge_width': 'boundary_width',
                                    'edge_type': 'boundary_type'})

    arg_dict_list = arg_df[['df', 'out_file', 'reference_im', 'geom_col',
                            'do_transform', 'channels', 'burn_value,'
                            'boundary_width', 'boundary_type',
                            'contact_spacing']
                           ].to_dict(orient='records')
    if not args.batch:
        result = df_to_px_mask(**arg_dict_list[0])
        if not args.output_path:
            return result

    else:
        with Pool(processes=args.workers) as pool:
            result = tqdm(pool.map(_func_wrapper, zip(repeat(df_to_px_mask),
                                                      arg_dict_list)))
            pool.close()


if __name__ == '__main__':
    main()