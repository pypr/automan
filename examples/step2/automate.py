from automan.api import Problem, Simulation, Automator


class Squares(Problem):
    def get_name(self):
        return 'squares'

    def setup(self):
        base_cmd = 'python square.py'
        self.cases = [
            Simulation(
                root=self.input_path('1'), base_command=base_cmd + ' 1',
            ),
            Simulation(
                root=self.input_path('2'), base_command=base_cmd + ' 2',
            ),
        ]

    def run(self):
        self.make_output_dir()


automator = Automator(
    simulation_dir='outputs',
    output_dir='manuscript/figures',
    all_problems=[Squares]
)
automator.run()
