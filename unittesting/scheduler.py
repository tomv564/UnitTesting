import os
import sublime
import sublime_plugin
from .utils import JsonFile


class Unit:

    def __init__(self, s):
        self.package = s['package']
        self.output = s['output'] if 'output' in s else None

        if 'syntax_test' in s and int(sublime.version()) >= 3000:
            self.syntax_test = s['syntax_test']
        else:
            self.syntax_test = False

        if 'color_scheme_test' in s and int(sublime.version()) >= 3000:
            self.color_scheme_test = s['color_scheme_test']
        else:
            self.color_scheme_test = False

        if 'coverage' in s and int(sublime.version()) >= 3103:
            self.coverage = s['coverage']
        else:
            self.coverage = False

    def run(self):
        if self.syntax_test:
            sublime.run_command("unit_testing_syntax", {
                "package": self.package,
                "output": self.output
            })
        elif self.color_scheme_test:
            sublime.run_command("unit_testing_color_scheme", {
                "package": self.package,
                "output": self.output
            })
        elif self.coverage:
                sublime.run_command("unit_testing_coverage", {
                    "package": self.package,
                    "output": self.output
                })
        else:
            sublime.run_command("unit_testing", {
                "package": self.package,
                "output": self.output
            })


class Scheduler:

    def __init__(self):
        self.units = []
        self.j = JsonFile(os.path.join(
            sublime.packages_path(),
            'User', 'UnitTesting',
            'schedule.json')
        )

    def load_schedule(self):
        self.schedule = self.j.load()
        for s in self.schedule:
            self.units.append(Unit(s))

    def run(self):
        self.load_schedule()
        for u in self.units:
            u.run()
        self.clean_schedule()

    def clean_schedule(self):
        self.j.save([])


class UnitTestingRunSchedulerCommand(sublime_plugin.ApplicationCommand):
    ready = False

    def run(self):
        UnitTestingRunSchedulerCommand.ready = True
        scheduler = Scheduler()
        scheduler.run()


class UnitTestingApiReadyCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        file_dir = os.path.join(sublime.packages_path(), "User", "UnitTesting")
        ready = os.path.join(file_dir, "ready")
        if not os.path.exists(ready):
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            open(ready, 'a').close()
