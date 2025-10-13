import request from "@/utils/request";
const MENU_BASE_URL = "/api/system/menus";

const MenuAPI = {
  /** 获取菜单树形列表 */
  getList(queryParams: MenuQuery) {
    return request<any, MenuVO[]>({ url: `${MENU_BASE_URL}/`, method: "get", params: queryParams });
  },
  /** 获取菜单下拉数据源 */
  getOptions(onlyParent?: boolean) {
    return request<any, OptionType[]>({
      url: `${MENU_BASE_URL}/`,
      method: "get",
      params: { onlyParent },
    });
  },
  /** 获取菜单表单数据 */
  getFormData(id: string) {
    return request<any, MenuForm>({ url: `${MENU_BASE_URL}/${id}/`, method: "get" });
  },
  /** 新增菜单 */
  create(data: MenuForm) {
    return request({ url: `${MENU_BASE_URL}/`, method: "post", data });
  },
  /** 修改菜单 */
  update(id: string, data: MenuForm) {
    return request({ url: `${MENU_BASE_URL}/${id}/`, method: "put", data });
  },
  /** 删除菜单 */
  deleteById(id: string) {
    return request({ url: `${MENU_BASE_URL}/${id}/`, method: "delete" });
  },
};

export default MenuAPI;

export interface MenuQuery {
  /** 搜索关键字 */
  search?: string;
}
// import type { MenuTypeEnum } from "@/enums/system/menu-enum";
export interface MenuVO {
  /** 子菜单 */
  children?: MenuVO[];
  /** 组件路径 */
  component?: string;
  /** ICON */
  icon?: string;
  /** 菜单ID */
  id?: string;
  /** 菜单名称 */
  name?: string;
  /** 父菜单ID */
  parent?: string;
  /** 按钮权限标识 */
  perm?: string;
  /** 跳转路径 */
  redirect?: string;
  /** 路由名称 */
  routeName?: string;
  /** 路由相对路径 */
  routePath?: string;
  /** 菜单排序(数字越小排名越靠前) */
  sort?: number;
  /** 菜单类型 */
  type?: string;
  /** 是否可见(1:显示;0:隐藏) */
  visible?: number;
}
export interface MenuForm {
  /** 菜单ID */
  id?: string;
  /** 父菜单ID */
  parent?: string;
  /** 菜单名称 */
  name?: string;
  /** 是否可见(1-是 0-否) */
  visible: number;
  /** ICON */
  icon?: string;
  /** 排序 */
  sort?: number;
  /** 路由名称 */
  routeName?: string;
  /** 路由路径 */
  routePath?: string;
  /** 组件路径 */
  component?: string;
  /** 跳转路由路径 */
  redirect?: string;
  /** 菜单类型 */
  type?: string;
  /** 权限标识 */
  perm?: string;
  /** 【菜单】是否开启页面缓存 */
  keepAlive?: number;
  /** 【目录】只有一个子路由是否始终显示 */
  alwaysShow?: number;
  /** 其他参数 */
  params?: KeyValue[];
}
interface KeyValue {
  key: string;
  value: string;
}
