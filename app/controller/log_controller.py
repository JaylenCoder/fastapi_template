from fastapi import APIRouter
from fastapi import Depends
from starlette.responses import StreamingResponse
from config.get_db import get_db
from app.service.login_service import get_current_user
from app.service.log_service import *
from app.entity.vo.log_vo import *
from utils.response_util import *
from utils.log_util import *
from utils.page_util import get_page_obj
from utils.common_util import bytes2file_response
from app.aspect.interface_auth import CheckUserInterfaceAuth
from app.annotation.log_annotation import log_decorator


logController = APIRouter(prefix='/log', dependencies=[Depends(get_current_user)])


@logController.post("/operation/get", dependencies=[Depends(CheckUserInterfaceAuth('monitor:operlog:list'))])
async def get_system_operation_log_list(request: Request, operation_log_page_query: OperLogPageObject, query_db: Session = Depends(get_db)):
    try:
        operation_log_query = OperLogQueryModel(**operation_log_page_query.dict())
        # 获取全量数据
        operation_log_query_result = OperationLogService.get_operation_log_list_services(query_db, operation_log_query)
        # 分页操作
        operation_log_page_query_result = get_page_obj(operation_log_query_result, operation_log_page_query.page, operation_log_page_query.page_size)
        
        return MyResponse(data=operation_log_page_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/operation/delete", dependencies=[Depends(CheckUserInterfaceAuth('monitor:operlog:remove'))])
@log_decorator(title='操作日志管理', business_type=3)
async def delete_system_operation_log(request: Request, delete_operation_log: DeleteOperLogModel, query_db: Session = Depends(get_db)):
    try:
        delete_operation_log_result = OperationLogService.delete_operation_log_services(query_db, delete_operation_log)
        if delete_operation_log_result.is_success:
            logger.log_info(delete_operation_log_result.message)
            return MyResponse(data=delete_operation_log_result, msg=delete_operation_log_result.message)
        else:
            logger.log_warning(delete_operation_log_result.message)
            return MyResponse(data="", msg=delete_operation_log_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/operation/clear", dependencies=[Depends(CheckUserInterfaceAuth('monitor:operlog:remove'))])
@log_decorator(title='操作日志管理', business_type=9)
async def clear_system_operation_log(request: Request, clear_operation_log: ClearOperLogModel, query_db: Session = Depends(get_db)):
    try:
        clear_operation_log_result = OperationLogService.clear_operation_log_services(query_db, clear_operation_log)
        if clear_operation_log_result.is_success:
            logger.log_info(clear_operation_log_result.message)
            return MyResponse(data=clear_operation_log_result, msg=clear_operation_log_result.message)
        else:
            logger.log_warning(clear_operation_log_result.message)
            return MyResponse(data="", msg=clear_operation_log_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.get("/operation/{oper_id}", dependencies=[Depends(CheckUserInterfaceAuth('monitor:operlog:query'))])
async def query_detail_system_operation_log(request: Request, oper_id: int, query_db: Session = Depends(get_db)):
    try:
        detail_operation_log_result = OperationLogService.detail_operation_log_services(query_db, oper_id)
        logger.log_info(f'获取oper_id为{oper_id}的信息成功')
        return MyResponse(data=detail_operation_log_result, msg='获取成功')
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/operation/export", dependencies=[Depends(CheckUserInterfaceAuth('monitor:operlog:export'))])
@log_decorator(title='操作日志管理', business_type=5)
async def export_system_operation_log_list(request: Request, operation_log_query: OperLogQueryModel, query_db: Session = Depends(get_db)):
    try:
        # 获取全量数据
        operation_log_query_result = OperationLogService.get_operation_log_list_services(query_db, operation_log_query)
        operation_log_export_result = await OperationLogService.export_operation_log_list_services(request, operation_log_query_result)
        logger.log_info('导出成功')
        return StreamingResponse(content=bytes2file_response(operation_log_export_result))
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/login/get", dependencies=[Depends(CheckUserInterfaceAuth('monitor:logininfor:list'))])
async def get_system_login_log_list(request: Request, login_log_page_query: LoginLogPageObject, query_db: Session = Depends(get_db)):
    try:
        login_log_query = LoginLogQueryModel(**login_log_page_query.dict())
        # 获取全量数据
        login_log_query_result = LoginLogService.get_login_log_list_services(query_db, login_log_query)
        # 分页操作
        login_log_page_query_result = get_page_obj(login_log_query_result, login_log_page_query.page, login_log_page_query.page_size)
        
        return MyResponse(data=login_log_page_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/login/delete", dependencies=[Depends(CheckUserInterfaceAuth('monitor:logininfor:remove'))])
@log_decorator(title='登录日志管理', business_type=3)
async def delete_system_login_log(request: Request, delete_login_log: DeleteLoginLogModel, query_db: Session = Depends(get_db)):
    try:
        delete_login_log_result = LoginLogService.delete_login_log_services(query_db, delete_login_log)
        if delete_login_log_result.is_success:
            logger.log_info(delete_login_log_result.message)
            return MyResponse(data=delete_login_log_result, msg=delete_login_log_result.message)
        else:
            logger.log_warning(delete_login_log_result.message)
            return MyResponse(data="", msg=delete_login_log_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/login/clear", dependencies=[Depends(CheckUserInterfaceAuth('monitor:logininfor:remove'))])
@log_decorator(title='登录日志管理', business_type=9)
async def clear_system_login_log(request: Request, clear_login_log: ClearLoginLogModel, query_db: Session = Depends(get_db)):
    try:
        clear_login_log_result = LoginLogService.clear_login_log_services(query_db, clear_login_log)
        if clear_login_log_result.is_success:
            logger.log_info(clear_login_log_result.message)
            return MyResponse(data=clear_login_log_result, msg=clear_login_log_result.message)
        else:
            logger.log_warning(clear_login_log_result.message)
            return MyResponse(data="", msg=clear_login_log_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/login/unlock", dependencies=[Depends(CheckUserInterfaceAuth('monitor:logininfor:unlock'))])
@log_decorator(title='登录日志管理', business_type=0)
async def clear_system_login_log(request: Request, unlock_user: UnlockUser, query_db: Session = Depends(get_db)):
    try:
        unlock_user_result = await LoginLogService.unlock_user_services(request, unlock_user)
        if unlock_user_result.is_success:
            logger.log_info(unlock_user_result.message)
            return MyResponse(data=unlock_user_result, msg=unlock_user_result.message)
        else:
            logger.log_warning(unlock_user_result.message)
            return MyResponse(data="", msg=unlock_user_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@logController.post("/login/export", dependencies=[Depends(CheckUserInterfaceAuth('monitor:logininfor:export'))])
@log_decorator(title='登录日志管理', business_type=5)
async def export_system_login_log_list(request: Request, login_log_query: LoginLogQueryModel, query_db: Session = Depends(get_db)):
    try:
        # 获取全量数据
        login_log_query_result = LoginLogService.get_login_log_list_services(query_db, login_log_query)
        login_log_export_result = LoginLogService.export_login_log_list_services(login_log_query_result)
        logger.log_info('导出成功')
        return StreamingResponse(content=bytes2file_response(login_log_export_result))
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))
