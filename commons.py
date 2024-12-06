import constants, joblib, os, json, pandas as pd, numpy as np , io, requests


def get_reqd_intensity_data(wavelength,intensity):
    start_index, end_index = find_start_end_wavelength_indexes(wavelength)
    # Extract columns between the specified indices (inclusive)
    reqd_intensity_data = intensity.iloc[:, start_index:end_index + 1] 
    return reqd_intensity_data.values.tolist()

def find_start_end_wavelength_indexes(wavelength_df):
    wavelength_complete_list = wavelength_df.values.tolist()
    start_index = 0
    end_index = 0
    counter_index = -1
    for elem in wavelength_complete_list[0]:
        counter_index = counter_index+1
        if start_index == 0 and elem >= 400:
            start_index = counter_index
        elif end_index == 0 and elem >= 600:
            end_index = counter_index-1
            return start_index, end_index

def read_data_as_data_frame(new_data_file_path):
    print("Reading data")
    df = ""
    
    if new_data_file_path.startswith("http"): 
        try:
            response = requests.get(new_data_file_path)
            response.raise_for_status()  # ensure the request was successful
            
            data = response.json()
            df = pd.DataFrame(data)
            print(f"Data from URL loaded successfully: {len(df)} records")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the file from the URL: {e}")
    else:
    # for future compatibility with local files
        try:
            with open(new_data_file_path, 'r') as file:
                data = json.load(file)
                df = pd.DataFrame(data)
                print(f"Data from local file loaded successfully: {len(df)} records")
        except FileNotFoundError:
            print(f"File not found: {new_data_file_path}")
        except json.JSONDecodeError:
            print(f"Error reading the JSON content from file: {new_data_file_path}")

    return df

# def get_voc_label(input_str):
#     try:
#         if os.path.isfile(input_str):
#             # Check if the file path exists and is valid
#             file_name = get_file_name(input_str)
#             voc_name = get_voc_name(file_name)
#         else:
#             # Assume the input is directly the VOC name
#             voc_name = input_str

#         # Retrieve the VOC label from the map
#         return constants.TARGET_MAP[voc_name.upper().strip()]

#     except FileNotFoundError as fnfe:
#         print(f"Error: The file '{input_str}' does not exist.")
#         raise fnfe
#     except KeyError as ke:
#         print(f"Error: VOC name '{voc_name}' not found in constants.TARGET_MAP.")
#         raise ke
#     except Exception as e:
#         print(f"An unexpected error occurred while processing the file or VOC name: {e}")
#         raise e
    
# def get_voc_name(file_path):
#     file_name = os.path.basename(file_path)
#     return file_name[:file_name.find('_')].upper().strip()

# def get_file_name(file_path):
#     return os.path.basename(file_path)

def array_to_csv(results, results_file_path):
    directory = os.path.dirname(results_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    pd.DataFrame(np.array(results)).to_csv(results_file_path)
    return

def get_wavelength_intensity_test_data(test_data_file):
    df = read_data_as_data_frame(test_data_file)
    wavelength = pd.DataFrame([df['Spectrometer Cluster']['Spectrometer Wavelength Value']])
    intensity=pd.DataFrame(df['Spectrometer Cluster']['Spectrometer Intensity Value'])
    return wavelength, intensity
