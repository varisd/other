#!/bin/bash

model_file=$1
model_name="${model_file/.pkl/}"
config_file="${model_file/pkl/yaml}"

echo "fields:" > config/models/$config_file
cat config/fields.template >> config/models/$config_file
echo "" >> config/models/$config_file
echo "features:" >> config/models/$config_file
cat config/features.template >> config/models/$config_file
echo "" >> config/models/$config_file
echo "predict:" >> config/models/$config_file
cat config/predict.template >> config/models/$config_file
echo "" >> config/models/$config_file
echo "models:" >> config/models/$config_file
echo "	${model_name}: ${model_file}" >> config/models/$config_file
