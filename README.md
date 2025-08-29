Written by Dustin Mathia (dmathia@stanford.edu or dustin.mathia@gmail.com) during summer 2025 internship with professor Henning stehr.

### Requirements:
In requirements.txt:
 - dash
- numpy
- pandas
- openpyxl
- scipy
- dash-bootstrap-components
- dash-bootstrap-templates
- dash-ag-grid
### How to run:
To run gui program do ``app.py``
To get roc curve run module as script with:

    ```python3 -m validation-visualizer "file_name.tsv" "column_name"```

This will both print the output table in the terminal and save a tsv file of table. To change this behavior edit the ```__main__.py``` file.

> Written with [StackEdit](https://stackedit.io/).
