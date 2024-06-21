import pandas as pd

def update_excel(excel_path, row_index, col_index, new_urls):
    # Load the Excel file
    new_urls = list(new_urls)
    print(new_urls)
    # print(new_urls[0])
    df = pd.read_excel(excel_path, header=None)
    
    # Prepare the new data in the desired format
    new_data = [{'url': url} for url in new_urls]
    
    # Convert the list of dictionaries to a JSON-like string
    new_data_str = str(new_data).replace("'", '"')
    
    # Update the specified cell with the new data
    df.iloc[row_index, col_index] = new_data_str
    
    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_path, index=False, header=False)

# Example usage:
if __name__ == "__main__":
    excel_path = '/Users/yashshukla/Desktop/final_watermark/data/processed_excel/Untitled spreadsheet_processed.xlsx'
    row_index = 0  # specify the row index
    col_index = 0  # specify the column index
    new_urls = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    update_excel(excel_path, row_index, col_index, new_urls)
