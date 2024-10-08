from fastapi import APIRouter, Request
from fastapi import Depends, File, Form
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from config.env import CachePathConfig
from config.get_db import get_db
from app.service.login_service import get_current_user
from app.service.common_service import *
from app.service.config_service import ConfigService
from utils.response_util import *
from utils.log_util import *
from app.aspect.interface_auth import CheckUserInterfaceAuth
from typing import Optional


commonController = APIRouter()


@commonController.post("/upload", dependencies=[Depends(get_current_user), Depends(CheckUserInterfaceAuth('common'))])
async def common_upload(request: Request, taskPath: str = Form(), uploadId: str = Form(), file: UploadFile = File(...)):
    try:
        try:
            os.makedirs(os.path.join(CachePathConfig.PATH, taskPath, uploadId))
        except FileExistsError:
            pass
        CommonService.upload_service(CachePathConfig.PATH, taskPath, uploadId, file)
        logger.log_info('上传成功')
        return MyResponse(data={'filename': file.filename, 'path': f'/common/{CachePathConfig.PATHSTR}?taskPath={taskPath}&taskId={uploadId}&filename={file.filename}'}, msg="上传成功")
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@commonController.post("/uploadForEditor", dependencies=[Depends(get_current_user), Depends(CheckUserInterfaceAuth('common'))])
async def editor_upload(request: Request, baseUrl: str = Form(), uploadId: str = Form(), taskPath: str = Form(), file: UploadFile = File(...)):
    try:
        try:
            os.makedirs(os.path.join(CachePathConfig.PATH, taskPath, uploadId))
        except FileExistsError:
            pass
        CommonService.upload_service(CachePathConfig.PATH, taskPath, uploadId, file)
        logger.log_info('上传成功')
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    'errno': 0,
                    'data': {
                        'url': f'{baseUrl}/common/{CachePathConfig.PATHSTR}?taskPath={taskPath}&taskId={uploadId}&filename={file.filename}'
                    },
                }
            )
        )
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                {
                    'errno': 1,
                    'message': str(e),
                }
            )
        )


@commonController.get(f"/{CachePathConfig.PATHSTR}")
async def common_download(request: Request, taskPath: str, taskId: str, filename: str, token: Optional[str] = None, query_db: Session = Depends(get_db)):
    try:
        def generate_file():
            with open(os.path.join(CachePathConfig.PATH, taskPath, taskId, filename), 'rb') as response_file:
                yield from response_file
        if taskPath not in ['notice']:
            current_user = await get_current_user(request, token, query_db)
            if current_user:
                return StreamingResponse(content=generate_file())
        return StreamingResponse(content=generate_file())
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@commonController.get("/config/query/{config_key}")
async def query_system_config(request: Request, config_key: str):
    try:
        # 获取全量数据
        config_query_result = await ConfigService.query_config_list_from_cache_services(request.app.state.redis, config_key)
        
        return MyResponse(data=config_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))
