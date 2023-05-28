from ultralytics import YOLO
import torch
import json

model = YOLO("yolov8x.pt")


results = model(source = "0", show = False, device = torch.device("cpu") ,stream = True, verbose = False)
for result in results:
    boxes = result.boxes
    lables = {"content": []}
    for box in boxes:
        lables['content'].append(model.names.get(box.cls.item()))

    with open("objects.json", "w") as outfile:
        # write the dictionary to the file in JSON format
        json.dump(lables, outfile)