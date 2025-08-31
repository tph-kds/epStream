class BaseData:
    def __init__(self, config):
        self.config = config

    def __init_vars__(self):
        print(f"Initializing BaseData with config: {self.config}")

    def run_data_collection(self):
        pass 

    def stop_data_collection(self):
        pass

    def get_data(self):
        pass
