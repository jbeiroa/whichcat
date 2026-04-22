import torch
import torch.nn as nn
import torchvision.models as models

class WhichCatModel(nn.Module):
    def __init__(self, num_classes=2):
        super(WhichCatModel, self).__init__()
        # Using a pre-trained ResNet18 as a backbone for classification
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        # Replace the final fully connected layer
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.backbone(x)

if __name__ == "__main__":
    # Quick sanity check
    model = WhichCatModel()
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    print(f"Output shape: {output.shape}")
