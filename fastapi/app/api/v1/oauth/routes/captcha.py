"""OAuth 验证码 API 路由。"""

from fastapi import APIRouter, Request

from app.schemas.base import ResponseModel

router = APIRouter()

@router.get(
    "/captcha/",
    response_model=ResponseModel[dict],
    summary="获取验证码",
    description="""
## 获取图形验证码

生成并返回图形验证码，用于登录验证。

### 功能说明
1. 生成随机验证码
2. 返回验证码图片的 Base64 编码
3. 返回验证码缓存 key，用于后续验证

### 响应数据
- `captchaKey`: 验证码缓存 key，登录时需要传递
- `captchaBase64`: 验证码图片的 Base64 编码，可直接在 img 标签中使用

### 使用说明
1. 前端调用此接口获取验证码
2. 将 `captchaBase64` 设置为 img 标签的 src
3. 用户输入验证码后，将 `captchaKey` 和用户输入的验证码一起传递给登录接口
4. 验证码有效期通常为 5 分钟

### 示例
```html
<img src="data:image/png;base64,{captchaBase64}" />
```
    """,
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "captchaKey": "550e8400-e29b-41d4-a716-446655440000",
                            "captchaBase64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
                        }
                    }
                }
            }
        }
    }
)
async def get_captcha(
    request: Request,
) -> ResponseModel[dict]:
    import base64

    from captcha.image import ImageCaptcha

    from app.services.captcha_service import create_captcha

    # 创建验证码（自动存储到缓存）
    captcha_key, captcha_code = await create_captcha(length=4)

    # 生成验证码图片
    image = ImageCaptcha()
    data = image.generate(captcha_code)
    image_base64 = base64.b64encode(data.read()).decode()

    return ResponseModel.success(
        data={
            "captchaKey": captcha_key,
            "captchaBase64": f"data:image/png;base64,{image_base64}",
        }
    )

