import subprocess
import time
import os
import json

from helpers.ComfyUI_Controlnet_Aux import ComfyUI_Controlnet_Aux
from helpers.ComfyUI_AnimateDiff_Evolved import ComfyUI_AnimateDiff_Evolved

UPDATED_WEIGHTS_MANIFEST_URL = f"https://weights.replicate.delivery/default/comfy-ui/weights.json?cache_bypass={int(time.time())}"
UPDATED_WEIGHTS_MANIFEST_PATH = "updated_weights.json"
WEIGHTS_MANIFEST_PATH = "weights.json"

BASE_URL = "https://weights.replicate.delivery/default/comfy-ui"
BASE_PATH = "ComfyUI/models"


class WeightsManifest:
    def __init__(self):
        self.weights_manifest = self._load_weights_manifest()
        self.weights_map = self._initialize_weights_map()

    def _load_weights_manifest(self):
        self._download_updated_weights_manifest()
        return self._merge_manifests()

    def _download_updated_weights_manifest(self):
        if not os.path.exists(UPDATED_WEIGHTS_MANIFEST_PATH):
            print(
                f"Downloading updated weights manifest from {UPDATED_WEIGHTS_MANIFEST_URL}"
            )
            start = time.time()
            subprocess.check_call(
                [
                    "pget",
                    "--log-level",
                    "warn",
                    "-f",
                    UPDATED_WEIGHTS_MANIFEST_URL,
                    UPDATED_WEIGHTS_MANIFEST_PATH,
                ],
                close_fds=False,
            )
            print(
                f"Downloading {UPDATED_WEIGHTS_MANIFEST_URL} took: {(time.time() - start):.2f}s"
            )
        else:
            print("Updated weights manifest file already exists")

    def _merge_manifests(self):
        if os.path.exists(WEIGHTS_MANIFEST_PATH):
            with open(WEIGHTS_MANIFEST_PATH, "r") as f:
                original_manifest = json.load(f)
        else:
            original_manifest = {}

        with open(UPDATED_WEIGHTS_MANIFEST_PATH, "r") as f:
            updated_manifest = json.load(f)

        for key in updated_manifest:
            if key in original_manifest:
                for item in updated_manifest[key]:
                    if item not in original_manifest[key]:
                        print(f"Adding {item} to {key}")
                        original_manifest[key].append(item)
            else:
                original_manifest[key] = updated_manifest[key]

        return original_manifest

    def _generate_weights_map(self, keys, dest):
        return {
            key: {
                "url": f"{BASE_URL}/{dest}/{key}.tar",
                "dest": f"{BASE_PATH}/{dest}",
            }
            for key in keys
        }

    def _initialize_weights_map(self):
        weights_map = {}
        for key in self.weights_manifest.keys():
            if key.isupper():
                weights_map.update(
                    self._generate_weights_map(self.weights_manifest[key], key.lower())
                )
        weights_map.update(ComfyUI_Controlnet_Aux.weights_map(BASE_URL))
        weights_map.update(ComfyUI_AnimateDiff_Evolved.weights_map(BASE_URL))
        print("Allowed weights:")
        for weight in weights_map.keys():
            print(weight)

        return weights_map

    def non_commercial_weights(self):
        return [
            "inswapper_128.onnx",
            "inswapper_128_fp16.onnx",
            "proteus_v02.safetensors",
            "RealVisXL_V3.0_Turbo.safetensors",
            "sd_xl_turbo_1.0.safetensors",
            "sd_xl_turbo_1.0_fp16.safetensors",
            "svd.safetensors",
            "svd_xt.safetensors",
            "turbovisionxlSuperFastXLBasedOnNew_tvxlV32Bakedvae",
            "copaxTimelessxlSDXL1_v8.safetensors",
            "MODILL_XL_0.27_RC.safetensors",
        ]

    def is_non_commercial_only(self, weight_str):
        return weight_str in self.non_commercial_weights()

    def write_supported_weights(self):
        weight_lists = {
            "Checkpoints": self.weights_manifest.get("CHECKPOINTS", []),
            "Upscale models": self.weights_manifest.get("UPSCALE_MODELS", []),
            "CLIP Vision": self.weights_manifest.get("CLIP_VISION", []),
            "LORAs": self.weights_manifest.get("LORAS", []),
            "IPAdapter": self.weights_manifest.get("IPADAPTER", []),
            "ControlNet": self.weights_manifest.get("CONTROLNET", []),
            "VAE": self.weights_manifest.get("VAE", []),
            "PhotoMaker": self.weights_manifest.get("PHOTOMAKER", []),
            "InstantID": self.weights_manifest.get("INSTANTID", []),
            "InsightFace": self.weights_manifest.get("INSIGHTFACE", []),
            "Face restoration models": self.weights_manifest.get(
                "FACERESTORE_MODELS", []
            ),
            "Face detection models": self.weights_manifest.get("FACEDETECTION", []),
            "AnimateDiff": ComfyUI_AnimateDiff_Evolved.models(),
            "AnimateDiff LORAs": ComfyUI_AnimateDiff_Evolved.loras(),
            "ControlNet Preprocessors": sorted(
                {
                    f"{repo}/{filename}"
                    for filename, repo in ComfyUI_Controlnet_Aux.models().items()
                }
            ),
        }
        with open("supported_weights.md", "w") as f:
            for weight_type, weights in weight_lists.items():
                f.write(f"## {weight_type}\n\n")
                for weight in weights:
                    f.write(f"- {weight}\n")
                f.write("\n")
