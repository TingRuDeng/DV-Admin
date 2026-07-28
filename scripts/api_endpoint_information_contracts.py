from __future__ import annotations

from scripts.api_endpoint_contract_types import ContractEvidence, EndpointContract


INFORMATION_ENDPOINT_CONTRACTS: tuple[EndpointContract, ...] = (
    EndpointContract(
        key="information_profile",
        method="GET",
        path="/api/v1/information/profile/",
        auth_required=True,
        response_fields=("id", "username", "name", "avatar", "gender"),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/information/urls.py",
                ("profile/", "CentreAPIView"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/information/profile.py",
                ('@router.get("/profile/"', "UserProfile"),
            ),
            ContractEvidence(
                "frontend/src/api/information-api.ts",
                ("getProfile", "/profile/"),
            ),
        ),
    ),
    EndpointContract(
        key="information_profile_update",
        method="PUT",
        path="/api/v1/information/profile/",
        auth_required=True,
        request_fields=("name", "email", "mobile", "gender"),
        response_fields=("id", "username", "name"),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/information/views/centre.py",
                ("class CentreAPIView", "def put"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/information/profile.py",
                ('@router.put("/profile/"', "UpdateProfile"),
            ),
            ContractEvidence(
                "frontend/src/api/information-api.ts",
                ("updateProfile", 'method: "put"'),
            ),
        ),
    ),
    EndpointContract(
        key="information_password",
        method="PUT",
        path="/api/v1/information/password",
        auth_required=True,
        request_fields=("oldPassword", "newPassword", "confirmPassword"),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/information/urls.py",
                ("password", "ChangePasswordAPIView"),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/information/profile.py",
                ('@router.put("/password"', "ChangePassword"),
            ),
            ContractEvidence(
                "frontend/src/api/information-api.ts",
                ("changePassword", "/password", "oldPassword"),
            ),
        ),
    ),
    EndpointContract(
        key="information_avatar",
        method="POST",
        path="/api/v1/information/change-avatar/",
        auth_required=True,
        request_fields=("file",),
        response_fields=("avatar", "url"),
        evidence=(
            ContractEvidence(
                "backend/drf_admin/apps/information/views/centre.py",
                ("class ChangeAvatarAPIView", 'request.data.get("file")'),
            ),
            ContractEvidence(
                "fastapi/app/api/v1/information/profile.py",
                ('@router.post("/change-avatar/"', "file: UploadFile"),
            ),
            ContractEvidence(
                "frontend/src/api/information-api.ts",
                ("updateAvatar", 'formData.append("file"'),
            ),
        ),
    ),
)
