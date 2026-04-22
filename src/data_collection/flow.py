from metaflow import FlowSpec, step, Parameter
import os
from src.common.config import CAMERA_IPS

class DataCollectionFlow(FlowSpec):
    """
    Phase 1: Collect and filter frames from camera recordings.
    """
    
    camera_ips = Parameter('camera_ips', default=','.join(CAMERA_IPS), help='Comma-separated camera IPs')

    @step
    def start(self):
        """
        Initialize the data collection process.
        """
        self.ips = self.camera_ips.split(',')
        print(f"Starting data collection for cameras: {self.ips}")
        self.next(self.extract_frames)

    @step
    def extract_frames(self):
        """
        Extract frames from SD card recordings (placeholder logic).
        """
        # TODO: Implement SD card extraction via src.data_collection.extractor
        print("Extracting frames from SD card...")
        self.next(self.filter_cats)

    @step
    def filter_cats(self):
        """
        Filter frames that contain cats using a pre-trained PyTorch model.
        """
        # TODO: Implement filtering logic
        print("Filtering frames for cats...")
        self.next(self.end)

    @step
    def end(self):
        """
        Finish the flow.
        """
        print("Data collection flow completed.")

if __name__ == '__main__':
    DataCollectionFlow()
