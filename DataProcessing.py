import pandas as pd

def main(input_file_path, output_file_path):
    # file_path = "Divided_Data_By_Rate.xlsx"

    excel_file = pd.ExcelFile(input_file_path)
    sheet_names = excel_file.sheet_names
    print(sheet_names)

    # Define a function to process each sheet
    def process_sheet(sheet_name):
        # Load the data from the specific sheet
        df = pd.read_excel(input_file_path, sheet_name=sheet_name)
        
        # Sort the data by date
        df = df.sort_values(by='Date')
        
        df['Balance'] = 0  # Initialize a new Balance column with zeros
        
        for i in range(len(df)):
            if i == 0:
                # For the first row, just subtract Outward from Inward
                df.at[i, 'Balance'] = df.at[i, 'Inward'] - df.at[i, 'Outward']
            else:
                # For subsequent rows, add the previous balance to the current Inward and subtract Outward
                df.at[i, 'Balance'] = df.at[i-1, 'Balance'] + df.at[i, 'Inward'] - df.at[i, 'Outward']
        
        return df


    # Process each sheet
    processed_sheets = {sheet: process_sheet(sheet) for sheet in sheet_names}

    # Save processed data to a new Excel file
    # output_file_path = 'Processed_Data.xlsx'
    with pd.ExcelWriter(output_file_path) as writer:
        for sheet, data in processed_sheets.items():
            data.to_excel(writer, sheet_name=sheet, index=False)

if __name__ == "__main__":
    main()
