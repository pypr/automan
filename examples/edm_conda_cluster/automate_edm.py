from automan.api import Problem, Automator, Simulation
from automan.api import EDMClusterManager
from matplotlib import pyplot as plt
import numpy as np


class Squares(Problem):
    def get_name(self):
        return 'squares'

    def get_commands(self):
        commands = [(str(i), 'python square.py %d' % i, None)
                    for i in range(1, 8)]
        return commands

    def run(self):
        self.make_output_dir()
        data = []
        for i in range(1, 8):
            stdout = self.input_path(str(i), 'stdout.txt')
            with open(stdout) as f:
                values = [float(x) for x in f.read().split()]
                data.append(values)

        data = np.asarray(data)
        plt.plot(data[:, 0], data[:, 1], 'o-')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.savefig(self.output_path('squares.pdf'))


class Powers(Problem):
    def get_name(self):
        return 'powers'

    def setup(self):
        base_cmd = 'python powers.py --output-dir $output_dir'
        self.cases = [
            Simulation(
                root=self.input_path(str(i)),
                base_command=base_cmd,
                power=float(i)
            )
            for i in range(1, 5)
        ]

    def run(self):
        self.make_output_dir()
        for case in self.cases:
            data = np.load(case.input_path('results.npz'))
            plt.plot(
                data['x'], data['y'],
                label=r'$x^{{%.2f}}$' % case.params['power']
            )
        plt.grid()
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.savefig(self.output_path('powers.pdf'))


if __name__ == '__main__':
    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[Squares, Powers],
        cluster_manager_factory=EDMClusterManager
    )
    automator.run()
