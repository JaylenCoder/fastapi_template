import math
from typing import List

from pydantic import BaseModel


class PageModel(BaseModel):
    """
    分页模型
    """
    offset: int
    page: int
    page_size: int
    total: int
    has_next: bool


class PageObjectResponse(BaseModel):
    """
    用户管理列表分页查询返回模型
    """
    rows: List = []
    page: int
    page_size: int
    total: int
    has_next: bool


def get_page_info(offset: int, page: int, page_size: int, count: int):
    """
    根据分页参数获取分页信息
    :param offset: 起始数据位置
    :param page: 当前页码
    :param page_size: 当前页面数据量
    :param count: 数据总数
    :return: 分页信息对象
    """
    has_next = False
    if offset >= count:
        res_offset_1 = (page - 2) * page_size
        if res_offset_1 < 0:
            res_offset = 0
            res_page = 1
        else:
            res_offset = res_offset_1
            res_page = page - 1
    else:
        res_offset = offset
        if (res_offset + page_size) < count:
            has_next = True
        res_page = page

    result = dict(offset=res_offset, page=res_page, page_size=page_size, total=count, has_next=has_next)

    return PageModel(**result)


def get_page_obj(data_list: List, page: int, page_size: int):
    """
    输入数据列表data_list和分页信息，返回分页数据列表结果
    :param data_list: 原始数据列表
    :param page: 当前页码
    :param page_size: 当前页面数据量
    :return: 分页数据对象
    """
    # 计算起始索引和结束索引
    start = (page - 1) * page_size
    end = page * page_size

    # 根据计算得到的起始索引和结束索引对数据列表进行切片
    paginated_data = data_list[start:end]
    has_next = True if math.ceil(len(data_list) / page_size) > page else False

    result = dict(
        data=paginated_data,
        # page=page,
        # page_size=page_size,
        total=len(data_list),
        # has_next=has_next
    )

    return PageObjectResponse(**result)


