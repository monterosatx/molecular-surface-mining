mkdir -p data_preparation/00-raw_pdbs/
cp input_models/*pdb data_preparation/00-raw_pdbs/
for fn in input_models/*
do
    BN=$(basename $fn| cut -d'.' -f1)
    ./data_prepare_one.sh $BN\_A 
    ./compute_descriptors.sh $BN\_A
    ./predict_site.sh $BN\_A
done
