### Project Overview 📝
The "Validation Visualizer" is a data visualization project designed to help bioinformaticians, clinicians, and variant scientists analyze molecular test data. Its primary purpose is to find the optimal threshold for separating positively and negatively diagnosed populations in new molecular tests.

The application utilizes Python libraries like **Plotly Dash**, **Dash Bootstrap Components**, **NumPy**, **Pandas**, and **SciPy**. It provides a graphical user interface (GUI) to explore and validate molecular test results.

***

### Key Features and Functionality 🛠️

The program is a practical application that provides several visualization tools:

* **Data Visualization**: The core functionality includes plotting data in multiple formats: a **rug plot**, a **density histogram**, or a **statistical fit**. This allows users to visualize the distribution of their data.
* **ROC Curve Analysis**: The application calculates and plots a **Receiver Operating Characteristic (ROC) curve**, which is crucial for determining the performance of a diagnostic test. Users can interact with the ROC plot to set a threshold and see the impact on sensitivity and specificity.
* **Data Table**: An **AG Grid table** is included to allow users to view the raw data directly within the application.
* **User Interaction**: The GUI features sliders and dropdown menus for selecting data columns and adjusting the threshold. Users can click on points in the plots to dynamically update the threshold slider.

***

### How It Works 💻
The application is built using the Plotly Dash framework. Data is processed from `.tsv` files, which are checked for correct formatting and the required `reference_result` column. The `reference_result` column must contain values of -1, 0, 1, or be empty (NaN).

Upon uploading a file, the program performs several background calculations:
* It labels the data and generates an ROC curve.
* It fits statistical parameters to the data, which are used to generate the statistical fit plot.

These processed files are then saved in a local `data` folder to avoid re-processing on subsequent loads.

To run the application, you can use the command `app.py`. For command-line users, the `validation-visualizer` module can generate an ROC curve and save the output as a `.tsv` file by running `python3 -m validation-visualizer "file_name.tsv" "column_name"`.
