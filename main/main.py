from pyzbar import pyzbar
import cv2
from typing import Callable
import time
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# 静态目录
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content={"errno": 1, "errmsg": str(exc)},
    )

@app.get("/")
def read_root():
    htmlContent = ""
    with open('index.html', 'r') as file:
        htmlContent = file.read()
    return HTMLResponse(content=htmlContent, status_code=200)


@app.post("/decode")
def decodeImage(file: UploadFile = File(...)):
    res = detectImage(file)
    data = []
    if len(res) <= 0:
        return {"errno": 1, "errmsg": "识别失败"}
    else:
        for barcode in res:
            if barcode.type == 'QRCODE':
                data.append(barcode.data.decode("utf-8"))
    if len(data) <= 0:
        return {"errno": 1, "errmsg": "没有识别到二维码"}
    else:
        return {"errno": 0, "errmsg": "识别成功", "data": data}



# 用OpenCV和Python识别
def detectImage(imageFile):
    imageFile.seek(0)
    img_array = np.asarray(bytearray(imageFile.file.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    barcodes = pyzbar.decode(img)
    return barcodes

# 计算函数执行时间
def timeExec(name: str, func: Callable[[], None]) -> None:
    time_start = time.time()
    func()
    time_end = time.time()
    print(f"{name} used {time_end - time_start} second(s)")

