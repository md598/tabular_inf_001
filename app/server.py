import aiohttp
import asyncio
import uvicorn
from fastai2.vision.all import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from google_drive_downloader import GoogleDriveDownloader as gdd
import base64

#https://drive.google.com/file/d/1-5o0YpAMjnEiewakEdO4xBS9nncwQ9lw/view?usp=sharing
#https://drive.google.com/uc?export=download&id=DRIVE_FILE_ID
export_file_url = '1-5o0YpAMjnEiewakEdO4xBS9nncwQ9lw'
export_file_name = 'export.pkl'

classes = ['cats_motorcycle','cats_running','cats_space','dogs_cars','dogs_motorcycle','dogs_swimming']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        gdd.download_file_from_google_drive(file_id=url, dest_path=dest, unzip=True) 

#async def download_file(url, dest):
#    if dest.exists(): return
#    async with aiohttp.ClientSession() as session:
#        async with session.get(url) as response:
#            data = await response.read()
#            with open(dest, 'wb') as f:
#                f.write(data)
                             
async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = torch.load(path/export_file_name, map_location=torch.device('cpu'))
        learn.dls.device = 'cpu'
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
  img_data = await request.form()
#  img_bytes = await (img_data['file'].read()) ##original
  img_bytes = await (img_data['file']) 
  pred = learn.predict(BytesIO(img_bytes))[0]
  return JSONResponse({
      'results': str(pred)
  })

#@app.route('/analyze', methods=['POST'])
#async def analyze(request):
#  img_data = await request.form()
#  img_bytes = (img_data['file'])
#  bytes = base64.b64decode(img_bytes)
#  img = open_image(BytesIO(bytes))
#  pred = learn.predict(img)[0]
#  return JSONResponse({
#      'results': str(pred)
#  })


#@app.route("/upload", methods=["POST"])
#async def upload(request):
#    data = await request.form()
#    img_bytes = (data["img"])
#    bytes = base64.b64decode(img_bytes)
#    return predict_from_bytes(bytes)
  
#def predict_from_bytes(bytes):
#    img = open_image(BytesIO(bytes))
#    print (learn.model)
#    _,_,losses = learn.predict(img)
#    predictions = sorted(zip(classes, map(float, losses)), key=lambda p: p[1], reverse=True)
#    result_html1 = path/'static'/'result1.html'
#    result_html2 = path/'static'/'result2.html'
#    
#    result_html = str(result_html1.open().read() +str(predictions[0:2]) + result_html2.open().read())
#    return HTMLResponse(result_html)
  

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
