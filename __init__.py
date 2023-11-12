from multiprocca import start_multiprocessing
from multiprocca.proclauncher import MultiProcExecution
import ctypes
import io
import os
import platform
import sys
from functools import cache
import subprocess
from a_cv_imwrite_imread_plus import open_image_in_cv
import pandas as pd
import cv2

iswindows = "win" in platform.platform().lower()
if iswindows:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    creationflags = subprocess.CREATE_NO_WINDOW
    invisibledict = {
        "startupinfo": startupinfo,
        "creationflags": creationflags,
        "start_new_session": True,
    }
    from ctypes import wintypes

    windll = ctypes.LibraryLoader(ctypes.WinDLL)
    user32 = windll.user32
    kernel32 = windll.kernel32
    GetExitCodeProcess = windll.kernel32.GetExitCodeProcess
    _GetShortPathNameW = kernel32.GetShortPathNameW
    _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _GetShortPathNameW.restype = wintypes.DWORD
else:
    invisibledict = {}


@cache
def get_short_path_name(long_name):
    try:
        if not iswindows:
            return long_name
        output_buf_size = 4096
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        _ = _GetShortPathNameW(long_name, output_buf, output_buf_size)
        return output_buf.value
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        sys.stderr.flush()
        return long_name


def _parse_tesseract(pic, language, tesser_path, tesser_args=(), invisibledata=()):
    invisibledict = dict(invisibledata)

    def convert_np_array_to_png(img):
        img = open_image_in_cv(img, channels_in_output=4)
        is_success, buffer = cv2.imencode(".png", img)
        io_buf = io.BytesIO(buffer)
        return io_buf.getvalue()

    exec("import subprocess", globals())
    exec("import numpy as np", globals())
    exec("""from a_cv_imwrite_imread_plus import open_image_in_cv""", globals())
    exec("""import pandas as pd""", globals())
    exec("""import cv2""", globals())
    exec("""import io""", globals())
    exec("""import os""", globals())

    args = [
        tesser_path,
        "-c",
        "tessedit_create_tsv=1",
        *tesser_args,
        "-l",
        language,
        "-",
        "stdout",
    ]
    osenv = os.environ.copy()

    result = subprocess.run(
        args,
        env=osenv,
        input=convert_np_array_to_png(pic),
        capture_output=True,
        **invisibledict,
    )
    return result.stdout, result.stderr


def parse_tesseract(
    piclist,
    language,
    tesser_path,
    tesser_args=(),
    usecache=True,
    processes=5,
    chunks=1,
    print_stdout=False,
    print_stderr=True,
):
    r"""
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
    """

    tesser_pathshort = get_short_path_name(tesser_path)
    f = [
        MultiProcExecution(
            fu=_parse_tesseract,
            args=(
                pic,
                language,
                tesser_pathshort,
                tesser_args,
                tuple(invisibledict.items()),
            ),
            kwargstuple=(),
        )
        for pic in piclist
    ]
    form, raw = start_multiprocessing(
        f,
        usecache=usecache,
        processes=processes,
        chunks=chunks,
        print_stdout=print_stdout,
        print_stderr=print_stderr,
    )

    stdcols = [
        "level",
        "page_num",
        "block_num",
        "par_num",
        "line_num",
        "word_num",
        "left",
        "top",
        "width",
        "height",
        "conf",
        "text",
        "img_index",
    ]
    dfframes = []
    for k, v in form.items():
        vv = io.StringIO(
            "\n".join(v[0].strip().decode("utf-8", "backslashreplace").splitlines()[1:])
        )
        dfframes.append(
            pd.read_csv(
                vv,
                keep_default_na=False,
                engine="c",
                sep="\t",
                names=stdcols,
                encoding_errors="backslashreplace",
                on_bad_lines="warn",
            ).assign(img_index=k)
        )
    df = pd.concat(dfframes, ignore_index=True)
    df["middle_x"] = df.left + (df.width // 2)
    df["middle_y"] = df.top + (df.height // 2)
    df["conf"] = df["conf"].astype("Float64")
    df["start_x"] = df.left
    df["start_y"] = df.top
    df["end_x"] = df.left + df.width
    df["end_y"] = df.top + df.height
    df["area"] = df.width * df.height
    df.columns = [f"aa_{x}" for x in df.columns]
    return df
