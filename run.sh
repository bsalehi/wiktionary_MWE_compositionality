#!/bin/bash

#script that computes the compositionality of multiword expressions


#parameters
option = "1"
#input
MWE_file="data/MWEs.txt"
wikidump="data/wiki"
#output
oc_file="compositionality.txt"



python Compute.py $MWE_file $wikidump $option > $oc_file
