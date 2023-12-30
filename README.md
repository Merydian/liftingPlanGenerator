# Weightlifting Training Plan Generator

This Python program generates personalized weightlifting training plans based on user input and preferences. It calculates Body Mass Index (BMI), Basal Metabolic Rate (BMR), and estimates one-repetition maximums (1RM) for specified exercises. The generated training plan is outputted in both CSV format for easy integration with Google Calendar and an HTML file for visualizing the plan.

## Features

- **User Profile:** Collects user information such as name, gender, height, weight, age, and exercise test data.
  
- **BMI and BMR Calculation:** Calculates BMI and BMR based on user input, providing insights into body composition and caloric needs.

- **1RM Estimation:** Estimates one-repetition maximums for specified exercises using the Epley formula.

- **Rate of Perceived Exertion (RPE):** Utilizes RPE values to customize the training intensity of each exercise.

- **Training Plan Generation:** Creates a structured training plan for a specified number of days per week and weeks. The plan includes exercises, sets, reps, and estimated weights.

- **Google Calendar Integration:** Outputs a CSV file compatible with Google Calendar, allowing users to easily import their training plan.

- **HTML Plan Visualization:** Generates an HTML file providing a visual representation of the training plan for easy reference.

## Usage

1. **Install Dependencies:**
   ```bash
   pip install pandas tabulate bs4
   ```

2. **Run the Program:**
   ```bash
   python plan2html_calendar.py
   ```

3. **Input User Details:**
   - Follow the prompts to provide information about the user and exercise test data.

4. **Generated Output:**
   - The program will output a CSV file suitable for importing into Google Calendar (`plans/{name}_{date}_calendar.csv`) and an HTML file visualizing the training plan (`plans/{name}_{date}.html`).


## Dependencies

- `pandas`: Data manipulation and CSV file handling.
- `tabulate`: Formatting data into tables for HTML output.
- `beautifulsoup4`: HTML parsing for a cleaner output.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

Feel free to customize and adapt this program to suit your specific needs. If you encounter any issues or have suggestions for improvement, please [open an issue](https://github.com/merydian/liftingPlanGenerator/issues).

Happy lifting! 🏋️‍♂️
