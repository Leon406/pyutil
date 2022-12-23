import muggle_ocr
import time
import base64

sdk_Captcha = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
sdk_OCR = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)

if __name__ == '__main__':
    b64 = "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"
    t1 = time.time()
    with open(r"1.jpg", "rb") as f:
        print(sdk_Captcha.predict(f.read()), (time.time() - t1) * 1000)

    t1 = time.time()
    with open(r"1.jpg", "rb") as f:
        print(sdk_OCR.predict(f.read()), (time.time() - t1) * 1000)
    t1 = time.time()
    print(sdk_Captcha.predict(base64.b64decode(b64)), (time.time() - t1) * 1000)