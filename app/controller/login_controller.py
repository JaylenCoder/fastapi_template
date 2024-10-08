from fastapi import APIRouter
from app.service.login_service import *
from app.entity.vo.login_vo import *
from app.dao.login_dao import *
from config.env import JwtConfig, RedisInitKeyConfig
from utils.response_util import *
from utils.log_util import *
from app.aspect.interface_auth import CheckUserInterfaceAuth
from app.annotation.log_annotation import log_decorator
from datetime import timedelta


loginController = APIRouter()


@loginController.post("/loginByAccount")
@log_decorator(title='用户登录', business_type=0, log_type='login')
async def login(request: Request, form_data: CustomOAuth2PasswordRequestForm = Depends(), query_db: Session = Depends(get_db)):
    captcha_enabled = True if await request.app.state.redis.get(f"{RedisInitKeyConfig.SYS_CONFIG.get('key')}:sys.account.captchaEnabled") == 'true' else False
    user = UserLogin(
        **dict(
            user_name=form_data.username,
            password=form_data.password,
            captcha=form_data.captcha,
            session_id=form_data.session_id,
            login_info=form_data.login_info,
            captcha_enabled=captcha_enabled
        )
    )
    try:
        result = await authenticate_user(request, query_db, user)
    except LoginException as e:
        return MyResponse(data="", msg=e.message)
    try:
        access_token_expires = timedelta(minutes=JwtConfig.jwt_expire_minutes)
        session_id = str(uuid.uuid4())
        access_token = create_access_token(
            data={
                "user_id": str(result[0].user_id),
                "user_name": result[0].user_name,
                "dept_name": result[1].dept_name if result[1] else None,
                "session_id": session_id,
                "login_info": user.login_info
            },
            expires_delta=access_token_expires
        )
        if AppConfig.app_same_time_login:
            await request.app.state.redis.set(f"{RedisInitKeyConfig.ACCESS_TOKEN.get('key')}:{session_id}", access_token,
                                              ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes))
        else:
            # 此方法可实现同一账号同一时间只能登录一次
            await request.app.state.redis.set(f"{RedisInitKeyConfig.ACCESS_TOKEN.get('key')}:{result[0].user_id}", access_token,
                                              ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes))
        logger.log_info('登录成功')
        # 判断请求是否来自于api文档，如果是返回指定格式的结果，用于修复api文档认证成功后token显示undefined的bug
        request_from_swagger = request.headers.get('referer').endswith('docs') if request.headers.get('referer') else False
        request_from_redoc = request.headers.get('referer').endswith('redoc') if request.headers.get('referer') else False
        if request_from_swagger or request_from_redoc:
            return {'access_token': access_token, 'token_type': 'Bearer'}
        return MyResponse(
            data={'access_token': access_token, 'token_type': 'Bearer'},
            msg='登录成功'
        )
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@loginController.post("/getSmsCode")
async def get_sms_code(request: Request, user: ResetUserModel, query_db: Session = Depends(get_db)):
    try:
        sms_result = await get_sms_code_services(request, query_db, user)
        if sms_result.is_success:
            
            return MyResponse(data=sms_result, msg='获取成功')
        else:
            logger.log_warning(sms_result.message)
            return MyResponse(data='', msg=sms_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@loginController.post("/forgetPwd")
async def forget_user_pwd(request: Request, forget_user: ResetUserModel, query_db: Session = Depends(get_db)):
    try:
        forget_user_result = await forget_user_services(request, query_db, forget_user)
        if forget_user_result.is_success:
            logger.log_info(forget_user_result.message)
            return MyResponse(data=forget_user_result, msg=forget_user_result.message)
        else:
            logger.log_warning(forget_user_result.message)
            return MyResponse(data="", msg=forget_user_result.message)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@loginController.post("/getLoginUserInfo", dependencies=[Depends(CheckUserInterfaceAuth('common'))])
async def get_login_user_info(request: Request, current_user: CurrentUserInfoServiceResponse = Depends(get_current_user)):
    try:
        
        return MyResponse(data=current_user)
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))


@loginController.post("/logout", dependencies=[Depends(get_current_user), Depends(CheckUserInterfaceAuth('common'))])
async def logout(request: Request, token: Optional[str] = Depends(oauth2_scheme), query_db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
        session_id: str = payload.get("session_id")
        await logout_services(request, session_id)
        logger.log_info('退出成功')
        return MyResponse(data="", msg="退出成功")
    except Exception as e:
        logger.exception(e)
        return MyResponse(data="", msg=str(e))
