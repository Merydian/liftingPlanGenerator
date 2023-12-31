from tabulate import tabulate
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta, date


class plan2html:
    def __init__(self, name, gender, h, m, a, test, days, weeks, start=None):
        """
        Initializes a plan2html object.

        Parameters:
        - name (str): Name of the user.
        - gender (str): Gender of the user ('m' or 'f').
        - h (int): Height of the user in centimeters.
        - m (int): Weight of the user in kilograms.
        - a (int): Age of the user.
        - test (dict): Dictionary containing exercise test details.
        - days (int): Number of training days per week.
        - weeks (int): Number of training weeks.
        - start (datetime): Start date of the training plan.
        """
        self.dd = None
        self.days = days
        self.name = name
        self.gender = gender
        self.a = a
        self.m = m
        self.h = h
        self.test = test
        self.bmr = None
        self.maxs = {}
        self.bmi = self.BMICalc()
        self.pro = round(self.m * 1.6)
        self.program = ""
        self.weeks = weeks
        self.deload = 7
        self.ov = 2.5
        self.lut = pd.read_csv("utils/rpe_table.csv", index_col=0, sep="|")
        self.start = start
        if start.weekday() != 0:
            raise Exception("Sorry, start must be a monday")

        self.getMaxs()
        self.BMRCalc()
        self.BMICalc()
        self.plan()
        self.calendar()

    def BMICalc(self):
        """
        Calculates BMI and categorizes it.

        Returns:
        - tuple: BMI value and corresponding category.
        """
        bmi = round(self.m / ((self.h) / 100) ** 2, 2)

        if bmi < 18:  # First step, is it less than 18?
            text = "Underweight"

        elif bmi <= 24:  # If it isn't is it less than or equal to 24?
            text = "Ideal"

        elif bmi <= 29:  # If not is it less than or equal to 29?
            text = "Overweight"

        elif bmi <= 39:  # If not is it less than or equal to 39?
            text = "Obese"

        else:  # If none of the above work, i.e. it is greater than 39, do this.
            text = "Extremely Obese"

        return bmi, text

    def BMRCalc(self):
        """
        Calculates BMR based on gender.
        """
        if self.gender == "f" or "female":
            self.bmr = round(
                (655 + (4.35 * self.m) + (4.7 * self.h) - (4.7 * self.a)) * 1.5
            )

        elif self.gender == "m" or "male":
            self.bmr = round(
                (66 + (6.2 * self.m) + (12.7 * self.h) - (6.76 * self.a)) * 1.5
            )

    def rm(self, w, r):
        """
        Calculates 1RM based on weight and reps.

        Parameters:
        - w (float): Weight used in the exercise.
        - r (int): Number of repetitions performed.

        Returns:
        - float: Calculated 1RM value.
        """
        x = w * (1 + (r / 30))
        y = (100 * w) / (101.3 - 2.6713 * r)
        z = w * r**0.10
        s = (x + y + z) / 3

        rm = w * (1 + (r / 30))

        return 2.5 * round(((rm + s) / 2 * 0.97725) / 2.5, 1)

    def getMaxs(self):
        """
        Calculates maximum weights for each exercise.
        """
        for i in self.test:
            w = self.test[i][0]
            r = self.test[i][1]
            max = self.rm(w, r)
            self.maxs[i] = max

    def rpe(self, exercise, rpe, sets, reps, week, ov, roundval=2.5, accessory=False):
        """
        Generates formatted HTML for each exercise.

        Parameters:
        - exercise (str): Name of the exercise.
        - rpe (float): Rate of perceived exertion.
        - sets (int): Number of sets.
        - reps (int or str): Number of repetitions or 'X' for AMRAP.
        - week (int): Current training week.
        - ov (float): Bi-Weekly overload value.
        - roundval (float): Value for rounding the weight.
        - accessory (bool): Flag indicating if the exercise is an accessory exercise.

        Returns:
        - str: Formatted HTML for the exercise.
        """
        reps = str(reps)
        if week % self.deload == 0 or week == 1:
            sets = round(sets / 2)
        if accessory:
            return (
                f"{exercise.title()}:linebreak{sets}x{reps} @{rpe}linebreaklinebreak"
            )
        else:
            return (
                f"bold{exercise.title()}"
                f":boldendlinebreak{sets}x"
                f"{reps}x{str(roundval *
                              round(((self.maxs[exercise] *
                                      self.lut.loc[rpe][reps])*0.95) / roundval) + ov)}"
                f"linebreaklinebreak"
            )

    def ueberblick(self):
        """
        Generates HTML summary of user details.

        Returns:
        - str: Formatted HTML summary.
        """
        header = [
            "Name",
            "Height [cm]",
            "Weight [Kg]",
            "Age",
            "BMR [KCal]",
            "Protein per day [g]",
            "BMI",
            "Bi-Weekly overload [Kg]",
        ]
        main = [
            self.name,
            str(self.h),
            str(self.m),
            self.a,
            self.bmr,
            self.pro,
            self.bmi[0],
            self.ov,
        ]

        return tabulate([header, main], tablefmt="html")

    def amrap_test(self):
        """
        Generates HTML table for AMRAP test results.

        Returns:
        - str: Formatted HTML table.
        """
        header = [""] + [i.title() for i in list(self.test.keys())]
        test = ["Test [Reps@Weight]"] + [
            ", ".join(str(y) for y in self.test[i][::-1]) for i in self.test
        ]
        rm = ["1RM-estimate [Kg]"] + [str(self.maxs[i]) for i in self.maxs]
        bw = ["Bw%"] + [str(round(i / self.m, 2)) for i in self.maxs.values()]

        return tabulate([header, test, rm, bw], tablefmt="html")

    def table_style(self):
        """
        Reads CSS style for HTML tables.

        Returns:
        - str: CSS style.
        """
        with open("utils/style.css") as file:
            style = file.read()

        return style

    def plan(self):
        """
        Generates HTML plan based on the number of days and weeks.
        """

        desc = [
            "[Sets xlinebreakReps xlinebreakWeight/RPE]"
        ]

        if self.days == 2:
            ov = 0

            for i in range(self.weeks):
                if i % 2 == 0:
                    ov += self.ov

                week = i + 1

                dayOne = [
                    self.rpe("benchpress", 7, 3, 10, week, ov)
                    + self.rpe("chest press", 8.5, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 4, 8, week, ov)
                    + self.rpe("lat pulldown", 7, 3, 5, week, ov)
                    + self.rpe("leg curls", 7, 5, 10, week, ov, accessory=True)
                    + self.rpe(
                        "seated calve raises", 8, 5, 12, week, ov, accessory=True
                    )
                    + self.rpe("back extension", 8, 5, 8, week, ov, accessory=True)
                ]

                dayTwo = [
                    self.rpe("squat", 7, 3, 8, week, ov)
                    + self.rpe("legpress", 8.5, 2, 8, week, ov, accessory=True)
                    + self.rpe("benchpress", 7, 3, 5, week, ov)
                    + self.rpe("lat pulldown", 8, 4, 10, week, ov)
                    + self.rpe(
                        "seated calve raises", 5, 5, 12, week, ov, accessory=True
                    )
                    + self.rpe("ab rollout", 8, 3, "X", week, ov, accessory=True)
                    + self.rpe("upright row", 7, 5, 10, week, ov, accessory=True)
                ]

                x = [[f"Woche: {week}", "Tag 1", "Tag 2"], desc + dayOne + dayTwo]
                self.program += tabulate(x, tablefmt="html")

        if self.days == 3:
            ov = 0

            for i in range(self.weeks):
                if i % 2 == 0:
                    ov += self.ov

                week = i + 1

                dayOne = [
                    self.rpe("benchpress", 7, 3, 10, week, ov)
                    + self.rpe("chest press", 8.5, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 4, 8, week, ov)
                    + self.rpe("lat pulldown", 7, 3, 5, week, ov)
                    + self.rpe("leg curls", 7, 5, 10, week, ov, accessory=True)
                    + self.rpe(
                        "seated calve raises", 8, 5, 12, week, ov, accessory=True
                    )
                    + self.rpe("back extension", 8, 5, 8, week, ov, accessory=True)
                ]

                dayTwo = [
                    self.rpe("squat", 7, 3, 8, week, ov)
                    + self.rpe("legpress", 8.5, 2, 8, week, ov, accessory=True)
                    + self.rpe("benchpress", 7, 3, 5, week, ov)
                    + self.rpe("lat pulldown", 8, 4, 10, week, ov)
                    + self.rpe(
                        "seated calve raises", 5, 5, 12, week, ov, accessory=True
                    )
                    + self.rpe("ab rollout", 8, 3, "X", week, ov, accessory=True)
                    + self.rpe("upright row", 7, 5, 10, week, ov, accessory=True)
                ]

                dayThree = [
                    self.rpe("lat pulldown", 8.5, 3, 10, week, ov)
                    + self.rpe("seated row", 7, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 3, 5, week, ov)
                    + self.rpe("benchpress", 8, 4, 10, week, ov)
                    + self.rpe("leg curls", 8, 5, 8, week, ov, accessory=True)
                    + self.rpe("lateral raises", 8, 5, 12, week, ov, accessory=True)
                ]

                x = [
                    [f"Week: {week}", "Day 1", "Day 2", "Day 3"],
                    desc + dayOne + dayTwo + dayThree,
                    ]
                self.program += tabulate(x, tablefmt="html")

        if self.days == 4:
            ov = 0

            for i in range(self.weeks):
                if i % 2 == 0:
                    ov += self.ov

                week = i + 1

                dayOne = [
                    self.rpe("lat pulldown", 8.5, 3, 10, week, ov)
                    + self.rpe("seated row", 7, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 3, 5, week, ov)
                    + self.rpe("benchpress", 8, 4, 10, week, ov)
                    + self.rpe("leg curls", 8, 5, 8, week, ov, accessory=True)
                    + self.rpe("lateral raises", 8, 5, 12, week, ov, accessory=True)
                ]

                dayTwo = [
                    self.rpe("lat pulldown", 8.5, 3, 10, week, ov)
                    + self.rpe("seated row", 7, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 3, 5, week, ov)
                    + self.rpe("benchpress", 8, 4, 10, week, ov)
                    + self.rpe("leg curls", 8, 5, 8, week, ov, accessory=True)
                    + self.rpe("lateral raises", 8, 5, 12, week, ov, accessory=True)
                ]

                dayThree = [
                    self.rpe("lat pulldown", 8.5, 3, 10, week, ov)
                    + self.rpe("seated row", 7, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 3, 5, week, ov)
                    + self.rpe("benchpress", 8, 4, 10, week, ov)
                    + self.rpe("leg curls", 8, 5, 8, week, ov, accessory=True)
                    + self.rpe("lateral raises", 8, 5, 12, week, ov, accessory=True)
                ]

                dayFour = [
                    self.rpe("lat pulldown", 8.5, 3, 10, week, ov)
                    + self.rpe("seated row", 7, 2, 12, week, ov, accessory=True)
                    + self.rpe("squat", 7, 3, 5, week, ov)
                    + self.rpe("benchpress", 8, 4, 10, week, ov)
                    + self.rpe("leg curls", 8, 5, 8, week, ov, accessory=True)
                    + self.rpe("lateral raises", 8, 5, 12, week, ov, accessory=True)
                ]

                x = [
                    [f"Week: {week}", "Day 1", "Day 2", "Day 3", "Day 4"],
                    desc + dayOne + dayTwo + dayThree + dayFour,
                    ]
                self.program += tabulate(x, tablefmt="html")

    def annotation(self):
        """
        Generates HTML annotations with exercise links.

        Returns:
        - str: Formatted HTML annotations.
        """
        def anno(exercise, link):
            return f'<a href="{link}">{exercise}</a>'

        annos = [
            anno(
                "Benchpress",
                "https://exrx.net/WeightExercises/PectoralSternal/BBBenchPress",
            ),
            anno(
                "Cableflys",
                "https://exrx.net/WeightExercises/PectoralSternal/CBStandingFly",
            ),
            anno(
                "Lat Pulldown",
                "https://exrx.net/WeightExercises/LatissimusDorsi/CBFrontPulldown",
            ),
            anno(
                "Face Pulls",
                "https://exrx.net/WeightExercises/DeltoidPosterior/CBStandingRearDeltRowRope",
            ),
            anno(
                "Triceps Extensions",
                "https://exrx.net/WeightExercises/Triceps/CBTriExt",
            ),
            anno(
                "Overhead Press",
                "https://exrx.net/WeightExercises/DeltoidAnterior/BBMilitaryPress",
            ),
            anno(
                "Cable Row",
                "https://exrx.net/WeightExercises/BackGeneral/CBStraightBackSeatedRow",
            ),
            anno(
                "Skull Crusher",
                "https://exrx.net/WeightExercises/Triceps/BBLyingTriExtSC",
            ),
            anno("Squats", "https://exrx.net/WeightExercises/Quadriceps/BBSquat"),
            anno(
                "Hip Thrusts",
                "https://exrx.net/WeightExercises/GluteusMaximus/BBHipThrust",
            ),
            anno(
                "Legpress",
                "https://exrx.net/WeightExercises/Quadriceps/LVSeatedLegPress",
            ),
            anno(
                "Seated Calve Raise",
                "https://exrx.net/WeightExercises/Soleus/LVSeatedCalfRaise",
            ),
            anno(
                "Back Extensions",
                "https://exrx.net/WeightExercises/ErectorSpinae/WtBackExtension",
            ),
            anno(
                "Seated Leg Curls",
                "https://exrx.net/WeightExercises/Hamstrings/LVSeatedLegCurl",
            ),
            anno(
                "Lever Chest Press",
                "https://exrx.net/WeightExercises/PectoralSternal/LVChestPressS",
            ),
        ]

        return "<br>".join(annos)

    def calendar(self):
        """
        Generates a DataFrame for the calendar and populates it.
        """
        dd = pd.DataFrame(
            columns=[
                "Subject",
                "Start Date",
                "Start Time",
                "End Date",
                "End Time",
                "All Day Event",
                "Description",
                "Private",
            ]
        )
        df = pd.read_html(self.program)
        current_date = self.start
        for week in df:
            for i in range(self.days):
                workout = week[i + 1][1]
                workout = workout.replace("linebreak", "<br>")
                workout = workout.replace("bold", "")
                dd = dd._append(
                    {
                        "Subject": "Eurotraining",
                        "Start Date": current_date.strftime("%d/%m/%y"),
                        "Start Time": "8:00 Pm",
                        "End Date": current_date.strftime("%d/%m/%y"),
                        "End Time": "8:30 Pm",
                        "All Day Event": "False",
                        "Description": workout,
                        "Private": "True",
                    },
                    ignore_index=True,
                )

                if self.days == 2:
                    if i == 0:
                        current_date += timedelta(days=3)
                    else:
                        current_date += timedelta(days=4)
                if self.days == 3:
                    if i in [0, 1]:
                        current_date += timedelta(days=2)
                    else:
                        current_date += timedelta(days=3)
                elif self.days == 4:
                    if i in [0, 2]:
                        current_date += timedelta(days=1)
                    elif i == 1:
                        current_date += timedelta(days=2)
                    else:
                        current_date += timedelta(days=3)

            self.dd = dd

    def save(self):
        """
        Saves HTML and CSV files with user's plan and calendar.
        """
        ueberblick = "<h1>Überblick</h1>"
        test = "<h1>Test</h1>"
        plan = "<h1>Plan</h1>"
        uebungen = "<h1>Übungen (Links)</h1>"
        name = f"plans/{self.name}_{date.today()}.html"
        with open(name, "w") as file:
            text = (
                    self.table_style()
                    + ueberblick
                    + self.ueberblick()
                    + test
                    + self.amrap_test()
                    + plan
                    + self.program
                    + uebungen
                    + self.annotation()
            )
            text = (
                text.replace("linebreak", "<br>")
                .replace("boldend", "</b>")
                .replace("bold", "<b>")
            )
            soup = bs(text, features="html.parser")
            prettyHTML = soup.prettify()
            file.write(prettyHTML)
        print(f"HTML Plan saved at: {name}")

        name = f"plans/{self.name}_{date.today()}_calendar.csv"
        self.dd.to_csv(name, index=False)
        print(f"Calendar CSV saved at: {name}")


if __name__ == "__main__":
    rm = {"benchpress": (70, 8), "squat": (90, 10), "lat pulldown": (85, 10)}
    plan = plan2html("dummy", "m", 192, 95, 24, rm, 4, 10, datetime(2023, 12, 25))
    plan.save()