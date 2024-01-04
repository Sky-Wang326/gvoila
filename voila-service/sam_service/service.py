from segment_anything import SamPredictor, sam_model_registry
from .sam_utils import show_mask, show_points, bounding_box, adjust_bbox, show_box
import cv2
import numpy as np

SAM_CHECKPOINTS = {
    "vit_h": "change to your checkpoint path", 
    "vit_l": "change to your checkpoint path",
    "vit_b": "change to your checkpoint path",
}


class SAMService:
    def __init__(self, model_type, device='cuda:0'):
        self.model = sam_model_registry[model_type](checkpoint=SAM_CHECKPOINTS[model_type])
        self.model.to(device)
        self.predictor = SamPredictor(self.model)


    def _set_image(self, image, image_path=None):
        if image_path is not None:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.predictor.set_image(image)


    def get_attention(self, image, input_points, input_labels=None, nums=1):
        self._set_image(image)
        if input_labels is None:
            input_labels = np.ones(len(input_points))
        masks, scores, logits = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True,
        )
        sorted_scores = np.argsort(scores, axis=0)[::-1][:nums]
        return [bounding_box(masks[i]) for i in sorted_scores]

