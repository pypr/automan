from automan.api import Problem, Automator
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


automator = Automator(
    simulation_dir='outputs',
    output_dir='manuscript/figures',
    all_problems=[Squares]
)
automator.run()
