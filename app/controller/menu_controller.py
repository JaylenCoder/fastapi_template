from fastapi import APIRouter, Request
from fastapi import Depends
from config.get_db import get_db
from app.service.login_service import get_current_user
from app.service.menu_service import *
from app.entity.vo.menu_vo import *
from app.dao.menu_dao import *
from utils.response_util import *
from utils.log_util import *
from app.aspect.interface_auth import CheckUserInterfaceAuth
from app.annotation.log_annotation import log_decorator


menuController = APIRouter(dependencies=[Depends(get_current_user)])


@menuController.post("/menu/tree", dependencies=[Depends(CheckUserInterfaceAuth('common'))])
async def get_system_menu_tree(request: Request, menu_query: MenuTreeModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        menu_query_result = MenuService.get_menu_tree_services(query_db, menu_query, current_user)
        
        return MyResponse(data=menu_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@menuController.post("/menu/forEditOption", dependencies=[Depends(CheckUserInterfaceAuth('common'))])
async def get_system_menu_tree_for_edit_option(request: Request, menu_query: MenuModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        menu_query_result = MenuService.get_menu_tree_for_edit_option_services(query_db, menu_query, current_user)
        
        return MyResponse(data=menu_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@menuController.post("/menu/get", dependencies=[Depends(CheckUserInterfaceAuth('system:menu:list'))])
async def get_system_menu_list(request: Request, menu_query: MenuModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        menu_query_result = MenuService.get_menu_list_services(query_db, menu_query, current_user)
        
        return MyResponse(data=menu_query_result)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@menuController.post("/menu/add", dependencies=[Depends(CheckUserInterfaceAuth('system:menu:add'))])
@log_decorator(title='菜单管理', business_type=1)
async def add_system_menu(request: Request, add_menu: MenuModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        add_menu.create_by = current_user.user.user_name
        add_menu.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_menu.update_by = current_user.user.user_name
        add_menu.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_menu_result = MenuService.add_menu_services(query_db, add_menu)
        if add_menu_result.is_success:
            logger.log_info(add_menu_result.message)
            return MyResponse(data=add_menu_result, msg=add_menu_result.message)
        else:
            logger.log_warning(add_menu_result.message)
            return MyResponse(data="", msg=add_menu_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@menuController.patch("/menu/edit", dependencies=[Depends(CheckUserInterfaceAuth('system:menu:edit'))])
@log_decorator(title='菜单管理', business_type=2)
async def edit_system_menu(request: Request, edit_menu: MenuModel, query_db: Session = Depends(get_db), current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        edit_menu.update_by = current_user.user.user_name
        edit_menu.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        edit_menu_result = MenuService.edit_menu_services(query_db, edit_menu)
        if edit_menu_result.is_success:
            logger.log_info(edit_menu_result.message)
            return MyResponse(data=edit_menu_result, msg=edit_menu_result.message)
        else:
            logger.log_warning(edit_menu_result.message)
            return MyResponse(data="", msg=edit_menu_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@menuController.post("/menu/delete", dependencies=[Depends(CheckUserInterfaceAuth('system:menu:remove'))])
@log_decorator(title='菜单管理', business_type=3)
async def delete_system_menu(request: Request, delete_menu: DeleteMenuModel, query_db: Session = Depends(get_db)):
    try:
        delete_menu_result = MenuService.delete_menu_services(query_db, delete_menu)
        if delete_menu_result.is_success:
            logger.log_info(delete_menu_result.message)
            return MyResponse(data=delete_menu_result, msg=delete_menu_result.message)
        else:
            logger.log_warning(delete_menu_result.message)
            return MyResponse(data="", msg=delete_menu_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@menuController.get("/menu/{menu_id}", dependencies=[Depends(CheckUserInterfaceAuth('system:menu:query'))])
async def query_detail_system_menu(request: Request, menu_id: int, query_db: Session = Depends(get_db)):
    try:
        detail_menu_result = MenuService.detail_menu_services(query_db, menu_id)
        logger.log_info(f'获取menu_id为{menu_id}的信息成功')
        return MyResponse(data=detail_menu_result, msg='获取成功')
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))
