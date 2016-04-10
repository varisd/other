#!/bin/bash

test_file=$1
output_dir=$2

targets="new_node_pos new_node_prontype new_node_numtype new_node_numform new_node_numvalue new_node_adpostype new_node_conjtype new_node_poss new_node_reflex new_node_abbr new_node_hyph new_node_negativeness new_node_gender new_node_animateness new_node_number new_node_case new_node_prepcase new_node_degree new_node_person new_node_possgender new_node_possnumber new_node_verbform new_node_mood new_node_tense new_node_voice new_node_aspect new_node_variant new_node_style new_node_tagset new_node_other"

targets_str=$(echo $targets | tr ' ' '|')

# test models
for model_file in `ls models | grep "pkl$"`; do
    mem=30g
    output_file="${model_file/pkl/eval.out}"
    if [[ $model_file == extra_trees* || $model_file == random_forest* ]]; then mem=100g; fi
    ~bojar/tools/shell/qsubmit --mem=$mem "scripts/test_model.py models/$model_file $test_file '$targets_str' > ${output_dir}/$output_file"
    echo $output_file
done
