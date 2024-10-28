masif_seed_root=$(git rev-parse --show-toplevel)
masif_seed_search_root=$masif_seed_root/masif_seed_search
masif_root=$masif_seed_root/masif
masif_target_root=$masif_seed_search_root/data/masif_mimicry_targets/
export masif_db_root=../../../../../masif/
masif_source=$masif_root/source/
masif_data=$masif_root/data/
export masif_root
export masif_target_root
export PYTHONPATH=$PYTHONPATH:$masif_source:`pwd`
python -W ignore color_by_fingerprint_similarity.py $1
