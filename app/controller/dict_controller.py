from fastapi import APIRouter
from fastapi import Depends
from config.get_db import get_db
from app.service.login_service import get_current_user, CurrentUserInfoServiceResponse
from app.service.dict_service import *
from app.entity.vo.dict_vo import *
from utils.response_util import *
from utils.log_util import *
from utils.page_util import get_page_obj
from utils.common_util import bytes2file_response
from app.aspect.interface_auth import CheckUserInterfaceAuth
from app.annotation.log_annotation import log_decorator


dictController = APIRouter(dependencies=[Depends(get_current_user)])


@dictController.post("/dictType/get", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:list'))])
async def get_system_dict_type_list(request: Request, dict_type_page_query: DictTypePageObject, query_db: Session = Depends(get_db)):
    try:
        dict_type_query = DictTypeQueryModel(**dict_type_page_query.dict())
        # 获取全量数据
        dict_type_query_result = DictTypeService.get_dict_type_list_services(query_db, dict_type_query)
        # 分页操作
        dict_type_page_query_result = get_page_obj(dict_type_query_result, dict_type_page_query.page, dict_type_page_query.page_size)
        
        return MyResponse(data=dict_type_page_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictType/all", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:list'))])
async def get_system_all_dict_type(request: Request, dict_type_query: DictTypeQueryModel, query_db: Session = Depends(get_db)):
    try:
        dict_type_query_result = DictTypeService.get_all_dict_type_services(query_db)
        
        return MyResponse(data=dict_type_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictType/add", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:add'))])
@log_decorator(title='字典管理', business_type=1)
async def add_system_dict_type(request: Request, add_dict_type: DictTypeModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        add_dict_type.create_by = current_user.user.user_name
        add_dict_type.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_dict_type.update_by = current_user.user.user_name
        add_dict_type.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_dict_type_result = await DictTypeService.add_dict_type_services(request, query_db, add_dict_type)
        if add_dict_type_result.is_success:
            logger.log_info(add_dict_type_result.message)
            return MyResponse(data=add_dict_type_result, msg=add_dict_type_result.message)
        else:
            logger.log_warning(add_dict_type_result.message)
            return MyResponse(data="", msg=add_dict_type_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.patch("/dictType/edit", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:edit'))])
@log_decorator(title='字典管理', business_type=2)
async def edit_system_dict_type(request: Request, edit_dict_type: DictTypeModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        edit_dict_type.update_by = current_user.user.user_name
        edit_dict_type.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        edit_dict_type_result = await DictTypeService.edit_dict_type_services(request, query_db, edit_dict_type)
        if edit_dict_type_result.is_success:
            logger.log_info(edit_dict_type_result.message)
            return MyResponse(data=edit_dict_type_result, msg=edit_dict_type_result.message)
        else:
            logger.log_warning(edit_dict_type_result.message)
            return MyResponse(data="", msg=edit_dict_type_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictType/delete", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:remove'))])
@log_decorator(title='字典管理', business_type=3)
async def delete_system_dict_type(request: Request, delete_dict_type: DeleteDictTypeModel, query_db: Session = Depends(get_db)):
    try:
        delete_dict_type_result = await DictTypeService.delete_dict_type_services(request, query_db, delete_dict_type)
        if delete_dict_type_result.is_success:
            logger.log_info(delete_dict_type_result.message)
            return MyResponse(data=delete_dict_type_result, msg=delete_dict_type_result.message)
        else:
            logger.log_warning(delete_dict_type_result.message)
            return MyResponse(data="", msg=delete_dict_type_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.get("/dictType/{dict_id}", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:query'))])
async def query_detail_system_dict_type(request: Request, dict_id: int, query_db: Session = Depends(get_db)):
    try:
        detail_dict_type_result = DictTypeService.detail_dict_type_services(query_db, dict_id)
        logger.log_info(f'获取dict_id为{dict_id}的信息成功')
        return MyResponse(data=detail_dict_type_result, msg='获取成功')
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictType/export", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:export'))])
@log_decorator(title='字典管理', business_type=5)
async def export_system_dict_type_list(request: Request, dict_type_query: DictTypeQueryModel, query_db: Session = Depends(get_db)):
    try:
        # 获取全量数据
        dict_type_query_result = DictTypeService.get_dict_type_list_services(query_db, dict_type_query)
        dict_type_export_result = DictTypeService.export_dict_type_list_services(dict_type_query_result)
        logger.log_info('导出成功')
        return StreamingResponse(content=bytes2file_response(dict_type_export_result))
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictType/refresh", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:edit'))])
@log_decorator(title='字典管理', business_type=2)
async def refresh_system_dict(request: Request, query_db: Session = Depends(get_db)):
    try:
        refresh_dict_result = await DictTypeService.refresh_sys_dict_services(request, query_db)
        if refresh_dict_result.is_success:
            logger.log_info(refresh_dict_result.message)
            return MyResponse(data=refresh_dict_result, msg=refresh_dict_result.message)
        else:
            logger.log_warning(refresh_dict_result.message)
            return MyResponse(data="", msg=refresh_dict_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictData/get", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:list'))])
async def get_system_dict_data_list(request: Request, dict_data_page_query: DictDataPageObject, query_db: Session = Depends(get_db)):
    try:
        dict_data_query = DictDataModel(**dict_data_page_query.dict())
        # 获取全量数据
        dict_data_query_result = DictDataService.get_dict_data_list_services(query_db, dict_data_query)
        # 分页操作
        dict_data_page_query_result = get_page_obj(dict_data_query_result, dict_data_page_query.page, dict_data_page_query.page_size)
        
        return MyResponse(data=dict_data_page_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.get("/dictData/query/{dict_type}", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:list'))])
async def query_system_dict_data_list(request: Request, dict_type: str, query_db: Session = Depends(get_db)):
    try:
        # 获取全量数据
        dict_data_query_result = await DictDataService.query_dict_data_list_from_cache_services(request.app.state.redis, dict_type)
        
        return MyResponse(data=dict_data_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictData/add", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:add'))])
@log_decorator(title='字典管理', business_type=1)
async def add_system_dict_data(request: Request, add_dict_data: DictDataModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        add_dict_data.create_by = current_user.user.user_name
        add_dict_data.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_dict_data.update_by = current_user.user.user_name
        add_dict_data.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_dict_data_result = await DictDataService.add_dict_data_services(request, query_db, add_dict_data)
        if add_dict_data_result.is_success:
            logger.log_info(add_dict_data_result.message)
            return MyResponse(data=add_dict_data_result, msg=add_dict_data_result.message)
        else:
            logger.log_warning(add_dict_data_result.message)
            return MyResponse(data="", msg=add_dict_data_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.patch("/dictData/edit", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:edit'))])
@log_decorator(title='字典管理', business_type=2)
async def edit_system_dict_data(request: Request, edit_dict_data: DictDataModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        edit_dict_data.update_by = current_user.user.user_name
        edit_dict_data.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        edit_dict_data_result = await DictDataService.edit_dict_data_services(request, query_db, edit_dict_data)
        if edit_dict_data_result.is_success:
            logger.log_info(edit_dict_data_result.message)
            return MyResponse(data=edit_dict_data_result, msg=edit_dict_data_result.message)
        else:
            logger.log_warning(edit_dict_data_result.message)
            return MyResponse(data="", msg=edit_dict_data_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictData/delete", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:remove'))])
@log_decorator(title='字典管理', business_type=3)
async def delete_system_dict_data(request: Request, delete_dict_data: DeleteDictDataModel, query_db: Session = Depends(get_db)):
    try:
        delete_dict_data_result = await DictDataService.delete_dict_data_services(request, query_db, delete_dict_data)
        if delete_dict_data_result.is_success:
            logger.log_info(delete_dict_data_result.message)
            return MyResponse(data=delete_dict_data_result, msg=delete_dict_data_result.message)
        else:
            logger.log_warning(delete_dict_data_result.message)
            return MyResponse(data="", msg=delete_dict_data_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.get("/dictData/{dict_code}", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:query'))])
async def query_detail_system_dict_data(request: Request, dict_code: int, query_db: Session = Depends(get_db)):
    try:
        detail_dict_data_result = DictDataService.detail_dict_data_services(query_db, dict_code)
        logger.log_info(f'获取dict_code为{dict_code}的信息成功')
        return MyResponse(data=detail_dict_data_result, msg='获取成功')
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@dictController.post("/dictData/export", dependencies=[Depends(CheckUserInterfaceAuth('system:dict:export'))])
@log_decorator(title='字典管理', business_type=5)
async def export_system_dict_data_list(request: Request, dict_data_query: DictDataModel, query_db: Session = Depends(get_db)):
    try:
        # 获取全量数据
        dict_data_query_result = DictDataService.get_dict_data_list_services(query_db, dict_data_query)
        dict_data_export_result = DictDataService.export_dict_data_list_services(dict_data_query_result)
        logger.log_info('导出成功')
        return StreamingResponse(content=bytes2file_response(dict_data_export_result))
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))
