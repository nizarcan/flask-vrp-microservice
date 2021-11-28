from models.job import Job

class JobCollection:
    def __init__(self, job_list, location_count):
        # Initiating job list and other attributes  
        self.jobs = []

        self.demands = (location_count) * [0]
        self.service_times = (location_count) * [0]
        self.reverse_map = {}

        for job in job_list:
            self.add(job)
    
    def __len__(self):
        return len(self.jobs)

    def __iter__(self):
        return iter(self.jobs)

    def add(self, job_data):
        # Creating a new Job instance
        new_job = Job(job_data)

        # Demands and service times are pooled w.r.t. location.
        # Upon pooling, location-job info is kept in a dictionary.
        self.demands[new_job.location_idx] += new_job.demand
        self.service_times[new_job.location_idx] += new_job.service_time
        if new_job.location_idx in self.reverse_map.keys():
            self.reverse_map[new_job.location_idx].append(new_job.id)
        else:
            self.reverse_map[new_job.location_idx] = [new_job.id]
        self.jobs.append(new_job)
