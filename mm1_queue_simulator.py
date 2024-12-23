import argparse
import random
import numpy as np
import matplotlib.pyplot as plt

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


def theoretical_values(arr_rate, ser_rate):
    """
    Calculate theoretical metrics for M/M/1 queue.
    Returns:
        (float, float, float): Server utilization (ρ), average queue length (Lq), and average response time (W).
    """
    rho = arr_rate / ser_rate  # Server utilization
    if rho >= 1:
        raise ValueError("Arrival rate must be less than service rate for a stable system.")
    
    lq = rho**2 / (1 - rho)  # Average number in the queue
    w = 1 / (ser_rate - arr_rate)  # Average response time
    return rho, lq, w


if __name__ == "__main__":
    # Define the scenarios
    scenarios = [
        {"arr_rate": 0.5, "ser_rate": 1.0, "rho": 0.5},
        {"arr_rate": 0.7, "ser_rate": 1.0, "rho": 0.7},
        {"arr_rate": 0.9, "ser_rate": 1.0, "rho": 0.9},
    ]

    total_customers = 10000
    results = []

    for scenario in scenarios:
        arr_rate = scenario["arr_rate"]
        ser_rate = scenario["ser_rate"]
        rho_theoretical = scenario["rho"]

        # Calculate theoretical values
        rho, lq_theoretical, w_theoretical = theoretical_values(arr_rate, ser_rate)

        # Run simulation
        simulator = MM1QueueSimulator(arr_rate, ser_rate)
        simulator.simulate(total_customers)
        avg_queue_length, avg_response_time, server_utilization = simulator.metrics()

        # Store results
        results.append({
            "rho": rho_theoretical,
            "lq_theoretical": lq_theoretical,
            "w_theoretical": w_theoretical,
            "lq_simulated": avg_queue_length,
            "w_simulated": avg_response_time,
            "utilization_simulated": server_utilization,
            "queue_lengths": simulator.queue_lengths,
        })

    # Print results
    for result in results:
        print(f"ρ = {result['rho']:.1f}")
        print(f"Theoretical Average Queue Length (Lq): {result['lq_theoretical']:.2f}")
        print(f"Simulated Average Queue Length (Lq): {result['lq_simulated']:.2f}")
        print(f"Theoretical Average Response Time (W): {result['w_theoretical']:.2f}")
        print(f"Simulated Average Response Time (W): {result['w_simulated']:.2f}")
        print(f"Simulated Server Utilization: {result['utilization_simulated']:.2%}")
        print("-" * 40)

        # Histogram of queue lengths
        plt.hist(result["queue_lengths"], bins=20, edgecolor='black')
        plt.title(f"Histogram of Queue Lengths (ρ = {result['rho']:.1f})")
        plt.xlabel("Queue Length")
        plt.ylabel("Frequency")
        plt.show()

    # Theoretical vs Simulated Comparison
    theoretical_lqs = [result["lq_theoretical"] for result in results]
    simulated_lqs = [result["lq_simulated"] for result in results]
    rhos = [result["rho"] for result in results]

    plt.figure(figsize=(10, 6))
    plt.plot(rhos, theoretical_lqs, label="Theoretical Lq", marker='o', linestyle='--')
    plt.plot(rhos, simulated_lqs, label="Simulated Lq", marker='o')
    plt.xlabel("ρ (Utilization)")
    plt.ylabel("Average Queue Length (Lq)")
    plt.title("Theoretical vs Simulated Queue Lengths")
    plt.legend()
    plt.grid()
    plt.show()