class Job:
    def __init__(self, job_data):
        """
        Deconstructing job_data dictionary into `Job` attributes
        """
        
        self.id = job_data["id"]
        self.location_idx = job_data["location_index"]
        self.demand = job_data["delivery"][0]
        self.service_time = job_data["service"]