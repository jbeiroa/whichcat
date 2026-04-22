from metaflow import FlowSpec, step, Parameter
import time
from src.common.config import CAMERA_IPS
from src.data_collection.extractor import RTSPExtractor

class DataCollectionFlow(FlowSpec):
    """
    Phase 1: Collect and filter frames from live RTSP feeds using YOLOv8.
    """
    
    camera_ips = Parameter('camera_ips', 
                          default=','.join(CAMERA_IPS), 
                          help='Comma-separated camera IPs')
    
    duration_hours = Parameter('duration_hours', 
                               default=24.0, 
                               help='How long to run the collection in hours')

    @step
    def start(self):
        """
        Initialize the data collection process.
        """
        self.ips = [ip.strip() for ip in self.camera_ips.split(',') if ip.strip()]
        print(f"Starting live data collection for cameras: {self.ips}")
        print(f"Target duration: {self.duration_hours} hours")
        self.next(self.collect_live)

    @step
    def collect_live(self):
        """
        Run the live extraction and filtering using YOLOv8.
        """
        extractor = RTSPExtractor()
        extractor.start(ips=self.ips)
        
        start_time = time.time()
        end_time = start_time + (self.duration_hours * 3600)
        
        try:
            while time.time() < end_time:
                remaining = int(end_time - time.time())
                if remaining % 60 == 0: # Print status every minute
                    print(f"Collection in progress... {remaining // 60} minutes remaining.")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Collection interrupted by user.")
        finally:
            extractor.stop()
            
        self.next(self.end)

    @step
    def end(self):
        """
        Finish the flow.
        """
        print("Data collection flow completed.")

if __name__ == '__main__':
    DataCollectionFlow()
