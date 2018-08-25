# gs-script

## Set up environment variable for model repository
set PYTHONPATH=<PATH_TO_MODELS>;<PATH_TO_MODELS>\slim

## Generate protobuf for at models/research/
protobuf-compiler above v3.3.0 required
protoc object_detection/protos/*.proto --python_out=.

## Generate xml image detail to csv
python xml_to_csv.py

## Generate tfRecord
add new category in class_text_to_int function
python generate_tfrecord.py

## Update object-detection.pbtxt
add new category

## Update ssdlite_mobilenet_v2_coco.config
update num_classes

## start model training
python train.py --logtostderr --train_dir=models/detect_monster_v2/training --pipeline_config_path=models/detect_monster_v2/ssdlite_mobilenet_v2_coco.config

## Save and export trained model
python export_inference_graph.py --input_type image_tensor --pipeline_config_path models/detect_monster_v2/ssdlite_mobilenet_v2_coco.config --trained_checkpoint_prefix models/detect_monster_v2/training/model.ckpt-3166 --output_directory models/detect_monster_v2/training

## References
https://becominghuman.ai/tensorflow-object-detection-api-tutorial-training-and-evaluating-custom-object-detector-ed2594afcf73
https://medium.com/@WuStangDan/step-by-step-tensorflow-object-detection-api-tutorial-part-4-training-the-model-68a9e5d5a333