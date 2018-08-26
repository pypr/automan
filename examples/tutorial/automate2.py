from automan.api import Problem, Automator


class Squares(Problem):
    def get_name(self):
        return 'squares'

    def get_commands(self):
        return [
            ('1', 'python square.py 1', None),
            ('2', 'python square.py 2', None),
            ('3', 'python square.py 3', None),
            ('4', 'python square.py 4', None),
        ]

    def run(self):
        self.make_output_dir()
        data = []
        for i in ('1', '2', '3', '4'):
            stdout = self.input_path(i, 'stdout.txt')
            with open(stdout) as f:
                data.append(f.read().split())

        output = self.output_path('output.txt')
        with open(output, 'w') as o:
            o.write(str(data))


if __name__ == '__main__':
    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[Squares]
    )

    automator.run()
