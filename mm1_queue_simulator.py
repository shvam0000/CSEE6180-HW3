import argparse
import random
import numpy as np

class MM1QueueSimulator:
    def __init__(self, arr_rate, ser_rate):
        self.arr_rate = arr_rate  # λ
        self.ser_rate = ser_rate  # μ
        self.time = 0.0
        self.event_list = []
        self.queue = []  
        self.res_times = []
        self.queue_lengths = [] 

    def exponential_random(self, rate):
        """
        Generate random numbers with exponential distribution.
        """
        return -np.log(1.0 - random.random()) / rate

    def schedule_event(self, event_time, event_type):
        """
        Schedule an event (arrival or departure).
        """
        self.event_list.append((event_time, event_type))
        self.event_list.sort(key=lambda x: x[0])

    def simulate(self, total_customers):
        """
        Simulate the M/M/1 queue.
        """
        self.schedule_event(self.time + self.exponential_random(self.arr_rate), 'arrival')

        cust_served = 0

        while cust_served < total_customers:
            self.time, event_type = self.event_list.pop(0)
            self.queue_lengths.append(len(self.queue))

            if event_type == 'arrival':
                self.queue.append(self.time)
                self.schedule_event(self.time + self.exponential_random(self.arr_rate), 'arrival')

                # Start service immediately if server is idle
                if len(self.queue) == 1:
                    service_time = self.exponential_random(self.ser_rate)
                    self.schedule_event(self.time + service_time, 'departure')
            elif event_type == 'departure':
                arrival_time = self.queue.pop(0)
                self.res_times.append(self.time - arrival_time)
                cust_served += 1

                if self.queue:
                    service_time = self.exponential_random(self.ser_rate)
                    self.schedule_event(self.time + service_time, 'departure')

    def metrics(self):
        """
        Compute performance metrics.
        """
        avg_queue_length = np.mean(self.queue_lengths)
        avg_response_time = np.mean(self.res_times)
        server_utilization = sum(self.res_times) / self.time
        return avg_queue_length, avg_response_time, server_utilization

if __name__ == "__main__":
    # Ask the user if they want to use command-line arguments
    use_cmd_args = input("[QUESTION] Do you want to use the command-line arguments you gave for parameters? (yes/no): ").strip().lower()

    if use_cmd_args == "yes":
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Simulate an M/M/1 queue system.")
        parser.add_argument("--arr_rate", type=float, required=True, help="Arrival rate (λ)")
        parser.add_argument("--ser_rate", type=float, required=True, help="Service rate (μ)")
        parser.add_argument("--total_customers", type=int, required=True, help="Number of customers to simulate")
        args = parser.parse_args()

        arr_rate = args.arr_rate
        ser_rate = args.ser_rate
        total_customers = args.total_customers
    else:
        # Use default parameters
        print("Using default parameters...")
        arr_rate = 0.8  # λ
        ser_rate = 1.0  # μ
        total_customers = 10000

    # Run simulation
    simulator = MM1QueueSimulator(arr_rate, ser_rate)
    simulator.simulate(total_customers)
    avg_queue_length, avg_response_time, server_utilization = simulator.metrics()

    print(f"[DATA] Average Queue Length: {avg_queue_length:.2f}")
    print(f"[DATA] Average Response Time: {avg_response_time:.2f}")
    print(f"[DATA] Server Utilization: {server_utilization:.2%}")