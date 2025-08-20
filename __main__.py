if __name__ == "__main__":
    import argparse
    import os
    import pandas as pd
    from .utils import label_data, make_roc_curve, plot_roc_curve

    parser = argparse.ArgumentParser(description="get roc curve as tsv file, input file must have 'reference_result' column, and must specify column as argument")
    parser.add_argument("input_file", help="tsv file with 'reference_result' column")
    parser.add_argument("column", help="name of column you want to get roc curve of")
    args=parser.parse_args()

    df_input = pd.read_csv(args.input_file, sep="\t")
    labeled_data = label_data(df_input)
    roc_curves = make_roc_curve(labeled_data)
    roc_column = roc_curves.get(args.column)

    _, df_roc = plot_roc_curve(roc_column, 0, True)
    df_output = df_roc.drop_duplicates()

    output_file = os.path.splitext(args.input_file)[0]+"."+args.column+".roc"+".tsv"
    df_output.to_csv(output_file, sep="\t", index=None)
    print(df_output.to_string(index=False))
