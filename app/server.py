import aiohttp
import asyncio
import uvicorn
from fastai.tabular.all import *
from io import BytesIO, StringIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from google_drive_downloader import GoogleDriveDownloader as gdd
import base64
import csv
import warnings
import os
warnings.filterwarnings('ignore')

#https://drive.google.com/uc?export=download&id=DRIVE_FILE_ID
#1H7ck0uM35KUxJXyKbxzH3YUgUsNrSISC # 9_features_8_21_2020_v1.pkl


export_file_url = '1H7ck0uM35KUxJXyKbxzH3YUgUsNrSISC'
export_file_name = 'export.pkl'

#classes = ['Cats on motorcycles','Cats running','Cats in space','Dogs in cars','Dogs on motorcycles','Dogs swimming']
classes = ['0','1','2','3','4','5','6','7','8','9','10','11']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        gdd.download_file_from_google_drive(file_id=url, dest_path=dest, unzip=True) 

                        
async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = torch.load(path/export_file_name, map_location=torch.device('cpu'))
        learn.dls.device = 'cpu'
        learn.to_fp32()
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

#Tabular inference:
@app.route('/analyze', methods=['POST'])
async def analyze(request):
  print('analyze begin')
  data = await request.form()
  content = await (data['file'].read())
  print(data['file'])
  print('asdf')
  print(content)
  s = str(content, 'utf-8')
  data = StringIO(s)
  df = pd.read_csv(data)
  learn = load_learner(path/export_file_name)
  # if we want to do GPU:
  # learn.model = learn.model.cuda()
  #dl = learn.dls.train_dl.new(df) #original
  dl = learn.dls.test_dl(df)
  _, __, y = learn.get_preds(dl=dl, with_decoded=True)
  print(y)
  #y is a tensor, convert to numpy
  preds = y.numpy()
  print(preds)
  print(preds.shape)
  df['predictions'] = preds
  #df = pd.concat([df, pd.DataFrame(preds)], axis=1)
  df.info()
  print('add preds')
  path_res = Path('app/static/')
  print(path_res)
  df.to_csv(path_res/'results.csv',index=False)
  print('inference done')
  #return FileResponse(path_res/'results.csv', media_type='csv')
  #return FileResponse(f'{path_res}/results.csv', media_type='csv')
  return FileResponse('app/static/results.csv', media_type='csv')


#@app.route('/analyze', methods=['POST'])
#async def analyze(request):
#  img_data = await request.form()
#  img_bytes = await (img_data['file'].read()) ##original
#  img = Image.open(BytesIO(img_bytes))
#  img_np = np.array(Image.open(BytesIO(img_bytes)))
#  print('img_np'), print(img_np)
#  print('pred time')
#  pred = learn.predict(img_np)[0]
#  print('pred'), print(pred)
#  print('pred_all'),print(learn.predict(img_np))
#  return JSONResponse({
#      'result': str(pred) ##original
# })

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
