# Image Processing and Text Extraction with Tesseract - multiprocessing

## pip install tesserparsing


## Tested against Python 3.11 / Windows 10


```python
Image Processing and Text Extraction with Tesseract

This module provides functions for image processing and text
extraction using Tesseract OCR. It includes the following functionalities:

1. **get_short_path_name(long_name):**
	- Retrieves the short path name for a given long file name, primarily on Windows.
	- Uses the `ctypes` library to call the `GetShortPathNameW` function.

2. **parse_tesseract:**
	- Utilizes Tesseract OCR to extract text from a list of images concurrently.
	- Supports multiprocessing with the `start_multiprocessing` and `MultiProcExecution` classes.
	- Handles caching, subprocess execution, and result formatting.
	- Returns a pandas DataFrame containing structured OCR results.

3. **_parse_tesseract:**
	- Internal function for parallel execution of Tesseract OCR on a single image.
	- Converts image data to PNG format and invokes Tesseract subprocess.
	- Returns the standard output and standard error of the subprocess.

4. **Example Usage:**
	- Demonstrates how to use `parse_tesseract` to extract text from a folder of PNG images.
	- Outputs a pandas DataFrame with structured OCR results.

Usage:
	from tesserparsing import parse_tesseract
	from list_all_files_recursively import get_folder_file_complete_path # optional
	folder = r"C:\testfolderall"
	piclist = [
		x.path for x in get_folder_file_complete_path(folder) if x.ext.lower() == ".png"
	]
	language = "por"
	tesser_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
	df = parse_tesseract(
		piclist,
		language,
		tesser_path,
		tesser_args=(),
		usecache=True,
		processes=5,
		chunks=1,
		print_stdout=False,
		print_stderr=True,
	)

	# df
	# Out[3]:
	#       aa_level  aa_page_num  aa_block_num  ...  aa_end_x  aa_end_y  aa_area
	# 0            1            1             0  ...      1600       720  1152000
	# 1            2            1             1  ...      1570        43    27684
	# 2            3            1             1  ...      1570        43    27684
	# 3            4            1             1  ...      1570        43    27684
	# 4            5            1             1  ...       100        43     1156
	#         ...          ...           ...  ...       ...       ...      ...
	# 5685         4            1             1  ...       130        44     1515
	# 5686         5            1             1  ...       130        44     1515
	# 5687         1            1             0  ...       115        27     3105
	# 5688         1            1             0  ...       112        21     2352
	# 5689         1            1             0  ...        81       105     8505
	# [5690 rows x 20 columns]

Note:
	This module requires the Tesseract OCR executable to be installed on the system.
	Ensure the necessary dependencies are installed before using these functions.


```