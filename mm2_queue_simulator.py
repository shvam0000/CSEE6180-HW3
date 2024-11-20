import random
import numpy as np
import matplotlib.pyplot as plt


class MMQueueSimulator:
    def __init__(self, arr_rate, ser_rate, num_servers=1):
        self.arr_rate = arr_rate  # λ
        self.ser_rate = ser_rate  # μ
        self.num_servers = num_servers
        self.time = 0.0
        self.event_list = []
        self.queue = []  
        self.res_times = []
        self.queue_lengths = [] 
        self.servers_busy = 0  # Track number of busy servers

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
        Simulate the M/M/c queue (c = num_servers).
        """
        # Schedule the first arrival event
        self.schedule_event(self.time + self.exponential_random(self.arr_rate), 'arrival')

        cust_served = 0

        while cust_served < total_customers:
            # Process the next event in the timeline
            self.time, event_type = self.event_list.pop(0)
            self.queue_lengths.append(len(self.queue))

            if event_type == 'arrival':
                # Customer arrives
                self.queue.append(self.time)
                self.schedule_event(self.time + self.exponential_random(self.arr_rate), 'arrival')

                # Start service if a server is available
                if self.servers_busy < self.num_servers:
                    self.start_service()
            elif event_type == 'departure':
                if self.queue:  # Ensure there is a customer in the queue
                    arrival_time = self.queue.pop(0)
                    self.res_times.append(self.time - arrival_time)
                    cust_served += 1
                    self.servers_busy -= 1

                    # Serve the next customer in the queue, if any
                    if self.queue:
                        self.start_service()

    def start_service(self):
        """
        Start serving a customer.
        """
        self.servers_busy += 1
        service_time = self.exponential_random(self.ser_rate)
        self.schedule_event(self.time + service_time, 'departure')

    def metrics(self):
        """
        Compute performance metrics.
        """
        avg_queue_length = np.mean(self.queue_lengths)
        avg_response_time = np.mean(self.res_times)
        server_utilization = (sum(self.res_times) / self.num_servers) / self.time
        return avg_queue_length, avg_response_time, server_utilization


def theoretical_values_mm1(arr_rate, ser_rate):
    """
    Calculate theoretical metrics for M/M/1 queue.
    Returns:
        (float, float, float): Server utilization (ρ), average queue length (Lq), and average response time (W).
    """
    rho = arr_rate / ser_rate
    if rho >= 1:
        raise ValueError("Arrival rate must be less than service rate for a stable system.")
    
    lq = rho**2 / (1 - rho)
    w = 1 / (ser_rate - arr_rate)
    return rho, lq, w


def theoretical_values_mm2(arr_rate, ser_rate):
    """
    Calculate theoretical metrics for M/M/2 queue.
    Returns:
        (float, float, float): Server utilization (ρ), average queue length (Lq), and average response time (W).
    """
    rho = arr_rate / (2 * ser_rate)
    if rho >= 1:
        raise ValueError("Arrival rate must be less than total service rate for a stable system.")
    
    p0 = 1 / (1 + (2 * rho) + ((2 * rho**2) / (2 * (1 - rho))))
    lq = ((rho**2) * p0) / (2 * (1 - rho))
    w = lq / arr_rate + 1 / ser_rate
    return rho, lq, w


if __name__ == "__main__":
    # Parameters for the comparison
    scenarios = [
        {"arr_rate": 0.8, "ser_rate": 1.0, "num_servers": 1},  # M/M/1
        {"arr_rate": 0.8, "ser_rate": 1.0, "num_servers": 2},  # M/M/2
    ]

    total_customers = 10000
    results = []

    for scenario in scenarios:
        arr_rate = scenario["arr_rate"]
        ser_rate = scenario["ser_rate"]
        num_servers = scenario["num_servers"]

        # Calculate theoretical values
        if num_servers == 1:
            rho, lq_theoretical, w_theoretical = theoretical_values_mm1(arr_rate, ser_rate)
        else:
            rho, lq_theoretical, w_theoretical = theoretical_values_mm2(arr_rate, ser_rate)

        # Run simulation
        simulator = MMQueueSimulator(arr_rate, ser_rate, num_servers=num_servers)
        simulator.simulate(total_customers)
        avg_queue_length, avg_response_time, server_utilization = simulator.metrics()

        # Store results
        results.append({
            "num_servers": num_servers,
            "rho": rho,
            "lq_theoretical": lq_theoretical,
            "w_theoretical": w_theoretical,
            "lq_simulated": avg_queue_length,
            "w_simulated": avg_response_time,
            "utilization_simulated": server_utilization,
            "queue_lengths": simulator.queue_lengths,
        })

    # Print results
    for result in results:
        print(f"System: M/M/{result['num_servers']}")
        print(f"Theoretical Average Queue Length (Lq): {result['lq_theoretical']:.2f}")
        print(f"Simulated Average Queue Length (Lq): {result['lq_simulated']:.2f}")
        print(f"Theoretical Average Response Time (W): {result['w_theoretical']:.2f}")
        print(f"Simulated Average Response Time (W): {result['w_simulated']:.2f}")
        print(f"Simulated Server Utilization: {result['utilization_simulated']:.2%}")
        print("-" * 40)

        # Histogram of queue lengths
        plt.hist(result["queue_lengths"], bins=20, edgecolor='black')
        plt.title(f"Histogram of Queue Lengths (M/M/{result['num_servers']})")
        plt.xlabel("Queue Length")
        plt.ylabel("Frequency")
        plt.show()

    # Comparison of Theoretical vs Simulated Queue Lengths
    labels = [f"M/M/{result['num_servers']}" for result in results]
    theoretical_lqs = [result["lq_theoretical"] for result in results]
    simulated_lqs = [result["lq_simulated"] for result in results]

    x = np.arange(len(labels))
    width = 0.35

    plt.bar(x - width/2, theoretical_lqs, width, label="Theoretical Lq")
    plt.bar(x + width/2, simulated_lqs, width, label="Simulated Lq")
    plt.xlabel("System")
    plt.ylabel("Average Queue Length (Lq)")
    plt.title("Theoretical vs Simulated Queue Lengths")
    plt.xticks(x, labels)
    plt.legend()
    plt.show()

    # Analysis (as comments):
    """
    Analysis:
    - M/M/2 reduces the average queue length (Lq) compared to M/M/1 with the same total service rate.
    - With two servers, the system can handle more arrivals simultaneously, leading to reduced response times (W).
    - The server utilization (ρ) for M/M/2 is lower per server but improves overall performance.
    """