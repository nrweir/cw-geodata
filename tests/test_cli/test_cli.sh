#!/bin/bash

#set -ev  # if any command in the script fails, the whole thing will fail

# empty output space
rm -rf cw-geodata/tests/test_cli/results && mkdir cw-geodata/tests/test_cli/results

# run tests
geotransform_footprints -s cw-geodata/cw_geodata/data/geotiff_labels.geojson -r cw-geodata/cw_geodata/data/sample_geotiff.tif -o cw-geodata/tests/test_cli/results/to_px_test.geojson -p -d 0
make_graphs -s cw-geodata/cw_geodata/data/sample_roads.geojson -o cw-geodata/tests/test_cli/results/sample_road_graph.pkl
make_masks -s cw-geodata/cw_geodata/data/sample.csv -r cw-geodata/cw_geodata/data/sample_geotiff.tif -o cw-geodata/tests/test_cli/results/sample_fp_mask.tif -g PolygonWKT_Pix -f
make_masks -s cw-geodata/cw_geodata/data/sample.csv -r cw-geodata/cw_geodata/data/sample_geotiff.tif -o cw-geodata/tests/test_cli/results/sample_b_inner_mask.tif -g PolygonWKT_Pix -e
make_masks -s cw-geodata/cw_geodata/data/sample.csv -r cw-geodata/cw_geodata/data/sample_geotiff.tif -o cw-geodata/tests/test_cli/results/sample_b_outer10_mask.tif -g PolygonWKT_Pix -e -et outer -ew 10
make_masks -s cw-geodata/cw_geodata/data/sample.csv -r cw-geodata/cw_geodata/data/sample_geotiff.tif -o cw-geodata/tests/test_cli/results/sample_c_mask.tif -g PolygonWKT_Pix -c -cs 10
make_masks -s cw-geodata/cw_geodata/data/sample.csv -r cw-geodata/cw_geodata/data/sample_geotiff.tif -o cw-geodata/tests/test_cli/results/sample_fbc_mask.tif -g PolygonWKT_Pix -f -c -e

diff cw-geodata/tests/test_cli/results/to_px_test.geojson cw-geodata/tests/test_cli/expected/gj_to_px_result.geojson
diff cw-geodata/tests/test_cli/results/sample_road_graph.pkl cw-geodata/tests/test_cli/expected/sample_graph.pkl
diff cw-geodata/tests/test_cli/results/sample_fp_mask.tif cw-geodata/tests/test_cli/expected/sample_fp_mask.tif
diff cw-geodata/tests/test_cli/results/sample_b_inner_mask.tif cw-geodata/tests/test_cli/expected/sample_b_inner_mask.tif
diff cw-geodata/tests/test_cli/results/sample_b_outer10_mask.tif cw-geodata/tests/test_cli/expected/sample_b_outer10_mask.tif
diff cw-geodata/tests/test_cli/results/sample_c_mask.tif cw-geodata/tests/test_cli/expected/sample_c_mask.tif
diff cw-geodata/tests/test_cli/results/sample_fbc_mask.tif cw-geodata/tests/test_cli/expected/sample_fbc_mask.tif
