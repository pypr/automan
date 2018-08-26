from automan.api import Problem, Automator


class Squares(Problem):
    def get_name(self):
        return 'squares'

    def get_commands(self):
        return [
            ('1', 'python square.py 1', None),
            ('2', 'python square.py 2', None),
        ]

    def run(self):
        self.make_output_dir()


automator = Automator(
    simulation_dir='outputs',
    output_dir='manuscript/figures',
    all_problems=[Squares]
)
automator.run()
